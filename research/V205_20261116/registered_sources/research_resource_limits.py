"""Checked process-local limits for research jobs, including 64-bit Windows HANDLEs."""
import ctypes
import os


def apply_limits(threads=3):
    if os.name == 'nt':
        from ctypes import wintypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.GetCurrentProcess.argtypes=[];kernel.GetCurrentProcess.restype=wintypes.HANDLE
        kernel.SetPriorityClass.argtypes=[wintypes.HANDLE,wintypes.DWORD]
        kernel.SetPriorityClass.restype=wintypes.BOOL
        kernel.GetPriorityClass.argtypes=[wintypes.HANDLE];kernel.GetPriorityClass.restype=wintypes.DWORD
        kernel.SetProcessAffinityMask.argtypes=[wintypes.HANDLE,ctypes.c_size_t]
        kernel.SetProcessAffinityMask.restype=wintypes.BOOL
        kernel.GetProcessAffinityMask.argtypes=[wintypes.HANDLE,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
        kernel.GetProcessAffinityMask.restype=wintypes.BOOL
        process=kernel.GetCurrentProcess();mask=16515072
        if not kernel.SetPriorityClass(process,0x4000):raise ctypes.WinError(ctypes.get_last_error())
        if not kernel.SetProcessAffinityMask(process,mask):raise ctypes.WinError(ctypes.get_last_error())
        actual,system=ctypes.c_size_t(),ctypes.c_size_t()
        if not kernel.GetProcessAffinityMask(process,ctypes.byref(actual),ctypes.byref(system)):
            raise ctypes.WinError(ctypes.get_last_error())
        priority=kernel.GetPriorityClass(process)
        assert actual.value==mask and priority==0x4000,(actual.value,priority)
        info=dict(pid=os.getpid(),priority='BelowNormal',priority_code=priority,affinity=actual.value)
    else:
        allowed=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,allowed[-6:])
        os.nice(10)
        info=dict(pid=os.getpid(),nice=os.nice(0),affinity=sorted(os.sched_getaffinity(0)))
    import numba
    numba.set_num_threads(threads)
    assert numba.get_num_threads()==threads
    info['numba_threads']=threads
    return info
