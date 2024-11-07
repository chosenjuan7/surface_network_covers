import os
import glob

def find_off_files(directory):
    off_files = glob.glob(os.path.join(directory, '*.off'))
    return off_files

def get_number_of_faces(off_file):
    with open(off_file, 'r') as file:
        header = file.readline().strip()
        if header != 'OFF':
            raise ValueError("Not a valid OFF file")

        counts = file.readline().strip().split()
        if len(counts) < 3:
            raise ValueError("Invalid OFF file format")

        num_faces = int(counts[1])
        return num_faces


if __name__ == "__main__":
    directory = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\TEST\\'
    off_files = find_off_files(directory)
    
    for off_file in off_files:
        number_of_ones = get_number_of_faces(off_file)
        filename = directory + os.path.splitext(os.path.basename(off_file))[0] + ".txt"
        
        with open(filename, 'w') as file:
            for _ in range(number_of_ones):
                file.write('1\n')
            print(f"Wrote {number_of_ones} ones to {filename}.")