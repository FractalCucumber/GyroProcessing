

from time import perf_counter, sleep

import numpy as np

import polars as pl

res = pl.read_csv(
    'D:/Work/Gyro2023_Git/6884_139_6.2_3.txt', has_header=False, 
    separator='\t',
    schema_overrides=[
        pl.Int32, pl.Int32, pl.Int32, pl.Int32, pl.Int32
        ],
    use_pyarrow=True)
# print(res.dtypes)
# t = perf_counter()
# res.write_parquet(
#     'D:/Work/Gyro2023_Git/6881.parquet',
#     compression_level=22,
#     # compression='brotli', #11
#     # compression='gzip' #10
#     # compression='lz4', #10
#     # compression='lzo', #10
#     compression='zstd', #22
#     # statistics=False
#     # use_pyarrow=True
#     )
# print(perf_counter() - t)
# exit(-5)

res = res.to_numpy().astype(np.int32)
xData = res[::5, 0].astype(np.int32)
yData = res[::5, 1].astype(np.int32)
# # убираю неинформативные участки кривой
# arr = np.array([5, 1, 2.02, 3.015, 4, 4.99, 6.03, 14, 44.2, 55, 65.1, 75, 86, 97, 555, 1554, 2556, 3554, 2557, 2465])
# print(f'{arr.tolist()}')
# print(np.diff(arr).tolist())
# res = np.diff(np.diff(arr))
# res = np.abs(np.diff(np.diff(arr)))
# print(res.tolist())
# # print(np.sort(res))
# mean = np.mean(res)
# print(mean)
# mediana = np.median(np.abs(res))
# print(mediana)
# # exit(-15)
# print('-------------------------------------------------')
# print(arr[[0, *np.where(res > mediana)[0] + 1, -1]].tolist())
# print('-------------------------------------------------')
# print(arr[[0, *np.where(res > mediana / 3)[0] + 1, -1]].tolist())
# print('-------------------------------------------------')
# print(arr[[0, *np.where(res != 0)[0] + 1, -1]].tolist())
# exit(-5)
print('xData', xData[:10], 'yData', yData[:10])

n_starts = np.int32(0)
start = np.int32(0)
end = np.int32(1)
active = True
dots_y = np.zeros(shape=(10), dtype=np.int32)
dots_y[0] = yData[0]
dots_y[1] = yData[1]
dots_x = np.zeros(shape=(10), dtype=np.int32)
dots_x[0] = 0
dots_x[1] = 1
thr = np.array([10])
max_err = np.empty(shape=(1))
while end < xData.size:
    print('------------------------------')
    print('end', end, 'start', start)
    print('xData[start:end]', xData[start:end + 1])
    print(dots_x[n_starts:n_starts + 2])
    print(yData[dots_x[n_starts:n_starts + 2]])
    approx = np.interp(
        xData[start:end + 1],
        dots_x[n_starts:n_starts + 2],
        yData[dots_x[n_starts:n_starts + 2]])
    print('approx', approx)
    max_err = np.abs(approx - yData[start:end + 1]).max(axis=0)
    approx2 = np.interp(
        xData[start:end + 2],
        dots_x[n_starts:n_starts + 2],
        yData[dots_x[n_starts:n_starts + 2]])
    print('approx2', approx2)
    max_err2 = np.abs(approx2 - yData[start:end + 2]).max(axis=0)
    print('max_err', max_err, max_err2)
    print('max_err > thr', max_err > thr)
    print('max_err2 > thr', max_err2 > thr)
    if max_err > thr and max_err2 > thr:
        start = end
        n_starts += 1
        # for i in range(end.size):
        # print('max_err', dots[n_starts - 1, 1:2])
        print('end[max_err > thr]', end)
        print(n_starts)
        dots_x[n_starts] = end # добавляю точки
        print('n_starts', n_starts)
        print('dots', dots_x)
        if n_starts > 9:
            print('break')
            break
    end += 1
    print(end)
print('dots', dots_x)
exit()

# n_starts = np.array([0, 0, 0])
# start = np.array([0, 0, 0])
# end = np.array([1, 1, 1])
# active = np.array([True, True, True])
# dots = np.zeros(shape=(10, 3), dtype=np.int32)
# dots[0, :] = [0, 0, 0]
# dots[0, :] = [1, 1, 1]
# thr = np.array([10, 1, 0.1])
# max_err = np.empty(shape=(3))
# while True:
#     for i in range(end.size):
#         print(xData[start[i]:end[i]])
#         print(dots[n_starts[i]:n_starts[i]+1, i])
#         print(yData[dots[n_starts[i]:n_starts[i]+1, i]])
#         approx = np.interp(
#             xData[start[i]:end[i]],
#             dots[n_starts[i]:n_starts[i]+1, i],
#             yData[dots[n_starts[i]:n_starts[i]+1, i]])
#         print(approx)
#         max_err[i] = np.abs(approx - yData[start[i]:end[i]]).max(axis=0)
#     print('max_err', max_err)
#     n_starts += max_err > thr
#     # for i in range(end.size):
#     # print('max_err', dots[n_starts - 1, 1:2])
#     print('end[max_err > thr]', end[max_err > thr])
#     print(n_starts)
#     if any(n_starts) > 9:
#         break
#     dots[n_starts - 1, max_err > thr] = end[max_err > thr] # добавляю точки
#     print(dots)
#     end += 1
#     print(end)
exit()

