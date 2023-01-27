import os.path

from mpmath import mp
from tqdm import tqdm
from multiprocessing import Process
import numpy

def iterate_over_dataset(sample_method, filenames, folder_path):
    for count, paper_folder in enumerate(tqdm(filenames)):
        abs_paper_folder_path = os.path.join(os.path.abspath(folder_path), paper_folder)
        for filename in (os.listdir(abs_paper_folder_path)):
            sample_method(filename)

def run(sample_method, folder_path):
    cpu_count = mp.cpu_count()
    print("availableCPU", cpu_count)
    cpu_used_count = cpu_count if 6 > cpu_count else 6
    filenames = os.listdir(folder_path)
    process_items_array = numpy.array_split(numpy.asarray(filenames), cpu_used_count)


    processes = []
    for i in range(cpu_used_count):
        processes.append(Process(target=iterate_over_dataset(sample_method, filenames), args=(process_items_array[i], i)))

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    return



if __name__ == "__main__":
    run(r"C:\Users\Tugce\PycharmProjects\pythonProject4\NLPProjekt\usable_dataset", print)




