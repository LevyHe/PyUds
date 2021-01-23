# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 22:25:22 2021

@author: levy.he
@file  : ProxyManager.py
"""

import pickle
import sys,os,io
from subprocess import Popen, PIPE
from traceback import format_exc

class RemoteError(Exception):
    def __str__(self):
        return ('\n' + '-'*75 + '\n' + str(self.args[0]) + '\n' + '-'*75)

def all_methods(obj):
    temp = []
    for name in dir(obj):
        func = getattr(obj, name)
        if callable(func) and name[0] != '_':
            temp.append(name)
    return temp


def convert_to_error(kind, result):
    if kind == '#ERROR':
        raise ValueError(result)
    elif kind in ('#TRACEBACK', '#UNSERIALIZABLE'):
        if not isinstance(result, str):
            raise TypeError(
                "Result {0!r} (kind '{1}') type is {2}, not str".format(
                    result, kind, type(result)))
        if kind == '#UNSERIALIZABLE':
            raise RemoteError('Unserializable message: %s' % result)
        else:
            raise RemoteError(result)
    else:
        raise ValueError('Unrecognized message type {!r}'.format(kind))

def dispatch(c, id, methodname, args=(), kwds={}):
    '''
    Send a message to manager using connection `c` and return response
    '''
    c.send((id, methodname, args, kwds))
    kind, result = c.recv()
    if kind == '#RETURN':
        return result
    convert_to_error(kind, result)


def err_print(*values, sep=' ', end='\n', flush=True):
    '''print the message to stderr'''
    msg = sep.join([str(v) for v in values])
    sys.stderr.write(msg + end)
    if flush:
        sys.stderr.flush()

def pack_data(args):
    '''pack the args to pickle bytes'''
    data = pickle.dumps(args)
    num = len(data)
    num_b = num.to_bytes(4,'little')
    all_num = ((num + 4 + 15)//16) * 16
    res = b'\0' * (all_num - num - 4)
    return num_b + data + res

def unpack_data(data):
    '''unpack the pickle bytes to args'''
    args = pickle.loads(data)
    return args

class Connection(object):
    '''
    reader: a BufferedReader, raw binary stream. example pipe
    writer: a BufferedWriter, raw binary stream. example pipe
    '''
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    def read_bytes(self):
        num_b = self.reader.read(4)
        num = int.from_bytes(num_b, 'little')
        r_num = (num + 4 + 15) // 16
        data = self.reader.read((r_num * 16) - 4)
        data = data[:num]
        return data

    def write_bytes(self, data):
        self.writer.write(data)
        self.writer.flush()

    def recv(self):
        data = self.read_bytes()
        if data:
            return unpack_data(data)
        return None

    def send(self, args):
        data = pack_data(args)
        # num = (len(data) + 15) / 16
        self.write_bytes(data)


class Token(object):
    '''
    Type to uniquely identify a shared object
    '''
    __slots__ = ('typeid', 'conn', 'id')

    def __init__(self, typeid, conn, id):
        (self.typeid, self.conn, self.id) = (typeid, conn, id)

    def __getstate__(self):
        return (self.typeid, self.conn, self.id)

    def __setstate__(self, state):
        (self.typeid, self.conn, self.id) = state

    def __repr__(self):
        return '%s(typeid=%r, conn=%r, id=%r)' % \
               (self.__class__.__name__, self.typeid, self.conn, self.id)


class BaseProxy(object):
    
    def __init__(self, token, manager=None, exposed=None):
        self._conn = token.conn
        self._typeid = token.typeid
        self._id = token.id
        self._token = token
        self._manager = manager

    def _callmethod(self, methodname, args=(), kwds={}):
        self._conn.send((self._id, methodname, args, kwds))
        kind, result = self._conn.recv()
        if kind == '#RETURN':
            return result
        convert_to_error(kind, result)

    def __reduce__(self):
        return (RebuildProxy, (PipeProxy, self._token, self._manager, self._exposed_))

def MakeProxyType(name, exposed):
    dic = {}
    for meth in exposed:
        exec('''def %s(self, *args, **kwds):
        return self._callmethod(%r, args, kwds)''' % (meth, meth), dic)

    ProxyType = type(name, (BaseProxy,), dic)
    ProxyType._exposed_ = exposed
    return ProxyType


def PipeProxy(token, server, exposed=None):
    ProxyType = MakeProxyType('PipeProxy[%s]' % token.typeid, exposed)
    proxy = ProxyType(token, server, exposed)
    return proxy


def RebuildProxy(func, token, server, exposed):
    return func(token, server, exposed)


class ProxyManager(object):

    _registry = {}
    _public = ('_create', '_get_methods')

    def __init__(self, reader, writer):
        self.conn = Connection(reader, writer)
        self.obj_list = {}

    def public_request(self, funcname, typeid, args, kwds={}):
        try:
            if funcname in self._public:
                func = getattr(self, funcname)
                result = func(typeid, *args, **kwds)
                msg = ('#RETURN', result)
            else:
                msg = ('#ERROR', 'request is not a public methodname')
        except Exception:
            msg = ('#TRACEBACK', format_exc())
        finally:
            try:
                self.conn.send(msg)
            except Exception:
                err_print("#REMOTE", format_exc())


    def call_handler(self, ident, funcname, args, kwds={}):
        try:
            obj, exposed = self.obj_list[ident]
            func = getattr(obj, funcname)
            result = func(*args, **kwds)
            msg = ('#RETURN', result)
        except:
            msg = ('#TRACEBACK', format_exc())
        finally:
            try:
                self.conn.send(msg)
            except Exception:
                err_print("#REMOTE",format_exc())

    def error_handler(self, funcname):
        msg = ('#UNSERIALIZABLE', funcname)
        try:
            self.conn.send(msg)
        except Exception:
            err_print("#REMOTE",format_exc())

    def serve_forever(self):
        try:
            while True:
                request = self.conn.recv()
                if request is None:
                    break
                ident, funcname, args, kwds = request
                if ident == None:
                    typeid = args[0]
                    self.public_request(funcname, typeid, args[1:], kwds)
                elif ident in self.obj_list:
                    self.call_handler(ident, funcname, args, kwds)
                else:
                    self.error_handler(funcname)
        except (KeyboardInterrupt, SystemExit, EOFError, OSError):
            pass
        except Exception:
            err_print(format_exc())

    def _get_conn(self):
        return self.conn

    def _create(self, typeid, *args, **kwds):
        caller, exposed = self._registry[typeid]
        obj = caller(*args, **kwds)
        ident = '%x' % id(obj)
        self.obj_list[ident] = (obj, exposed)
        return ident, tuple(exposed)

    @classmethod
    def register(cls, typeid, caller=None, proxytype=None):

        if '_registry' not in cls.__dict__:
            cls._registry = cls._registry.copy()

        exposed = all_methods(caller)
        cls._registry[typeid] = (caller, exposed)
        
        def temp(self, *args, **kwds):
            conn = self._get_conn()
            ident,  exposed = dispatch(conn, None, '_create', (typeid,)+args, kwds)
            token = Token(typeid, conn, ident)
            proxy = PipeProxy(token, self, exposed)
            return proxy
        temp.__name__ = typeid
        setattr(cls, typeid, temp)

def ServerForever(ServerType):
    reader = io.open(sys.stdin.fileno(), mode='rb', closefd=False)
    writer = io.open(sys.stdout.fileno(), mode='wb', closefd=False)
    t = ServerType(reader, writer)
    writer.write(b'start')
    writer.flush()
    t.serve_forever()


def ServerClient(cmd, ServerType):
    proc = Popen(cmd, shell=False, stderr=sys.stderr,
                  stdout=PIPE, stdin=PIPE, bufsize=16, universal_newlines=False)
    status = proc.stdout.read(5)
    if status != b'start':
        proc.kill()
        raise RemoteError('Remote server can not start')
    obj = ServerType(proc.stdout, proc.stdin)

    return proc, obj

if __name__ == "__main__":
    class TestServer(ProxyManager):
        pass
    class TestClass(object):
        def __init__(self):
            print('TestClass')

        def test1(self):
            return 'test1'

    TestServer.register('TestClass', TestClass)

    if len(sys.argv) > 1:
        print = err_print
        err_print('start',os.getpid())
        ServerForever(TestServer)
        err_print(os.getpid())
    else:
        cmd = ['python', 'ProxyManager.py', 'server']
        _proc, t = ServerClient(cmd, TestServer)
        try:
            test = t.TestClass()
            print(test.test1())
        except:
            print(format_exc())
        finally:
            pass
            _proc.stdout.close()
            _proc.stdin.close()
            _proc.kill()

        
