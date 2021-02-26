import os
import math
from template.page import *
from template.pageSet import *
from template.table import *
from template.tools import *

class Disk:
    def __init__(self, db_dir, table_name, num_columns, key_column):
        self.fn = table_name
        self.db_dir = db_dir
        self.table_dir = os.path.join(db_dir, "Tables", table_name)
        self.base_fn = os.path.join(self.table_dir, table_name + ".base")
        self.tail_fn = os.path.join(self.table_dir, table_name + ".tail")
        self.info_fn = os.path.join(self.table_dir, table_name + ".info")
        self.key_directory = os.path.join(self.table_dir, table_name + ".kd")
        self.next_key_directory_block = 0
        self.next_base_block = 0
        self.next_tail_block = 0
        if not self.__files_exist():
            self.num_columns = num_columns
            self.key_column = key_column
            self.next_base_rid = START_RID
            self.next_tail_rid = START_RID
            self.__create_files(num_columns, key_column)
        else:
            self.__read_file_info()

    @staticmethod
    def get_all_disks(db_dir):
        disks = {}
        tables_dir = os.path.join(db_dir, "Tables")
        if os.path.exists(tables_dir) and os.path.isdir(tables_dir):
            for d in os.listdir(tables_dir):
                disks[d] = Disk(db_dir, d, -1, -1)

        return disks

    def __files_exist(self):
        return os.path.exists(self.base_fn) and os.path.exists(
            self.tail_fn) and os.path.exists(self.info_fn) and os.path.exists(self.key_directory)

    def __create_files(self, num_columns, key_column):
        if not os.path.exists(self.table_dir):
            os.makedirs(os.path.join(self.table_dir))  # make Tables directory for db if it doesn't exist
        a = open(self.base_fn, "wb")
        a.close()
        b = open(self.tail_fn, "wb")
        b.close()
        c = open(self.info_fn, "wb")
        c.write(int.to_bytes(num_columns, length=8, byteorder="little"))
        c.write(int.to_bytes(key_column, length=8, byteorder="little"))
        c.write(int.to_bytes(START_RID, length=8, byteorder="little"))
        c.write(int.to_bytes(START_RID, length=8, byteorder="little"))
        c.write(int.to_bytes(self.next_base_block, length=8, byteorder="little"))
        c.write(int.to_bytes(self.next_tail_block, length=8, byteorder="little"))
        c.close()
        d = open(self.key_directory, "wb")
        d.close()

    def __read_file_info(self):
        f = open(self.info_fn, "rb")
        self.num_columns = int.from_bytes(f.read(8), byteorder="little")
        self.key_column = int.from_bytes(f.read(8), byteorder="little")
        self.num_records = int.from_bytes(f.read(8), byteorder="little")
        self.next_base_rid = int.from_bytes(f.read(8), byteorder="little")
        self.next_tail_rid = int.from_bytes(f.read(8), byteorder="little")
        self.next_base_block = int.from_bytes(f.read(8), byteorder="little")
        self.next_tail_block = int.from_bytes(f.read(8), byteorder="little")
        f.close()

    def read_table(self):
        keys, base_block_start, tail_block_starts = self.read_key_directory_data()
        table = Table(self.fn, self.num_columns, self.key_column)
        table.next_base_rid = self.next_base_rid
        table.next_tail_rid = self.next_tail_rid
        table.keys = keys
        table.brid_block_start = base_block_start
        table.trid_block_start = tail_block_starts
        return table

    def read_key_directory_data(self):
        keys = {}
        base_block_starts = {}
        tail_block_starts = {}
        with open(self.key_directory, "rb") as f:
            while True:
                data = f.read(KEY_DIRECTORY_SET_SIZE)
                if data:
                    self.next_key_directory_block += KEY_DIRECTORY_SET_SIZE
                    k = []
                    brids = []
                    trids = []
                    brid_block_starts = []
                    trid_block_starts = []
                    for i in range(RECORDS_PER_PAGE):
                        k.append(int.from_bytes(data[(i * 8):(i * 8) + 8], byteorder="little"))
                        brids.append(
                            int.from_bytes(data[PAGE_SIZE + (i * 8):PAGE_SIZE + (i * 8) + 8], byteorder="little"))
                        trids.append(int.from_bytes(data[(PAGE_SIZE * 2) + (i * 8):(PAGE_SIZE * 2) + (i * 8) + 8],
                                                    byteorder="little"))
                        brid_block_starts.append(
                            int.from_bytes(data[(PAGE_SIZE * 3) + (i * 8):(PAGE_SIZE * 3) + (i * 8) + 8],
                                           byteorder="little"))
                        trid_block_starts.append(
                            int.from_bytes(data[(PAGE_SIZE * 4) + (i * 8):(PAGE_SIZE * 4) + (i * 8) + 8],
                                           byteorder="little"))

                    for i in range(len(k)):
                        keys[k[i]] = brids[i]
                        base_block_starts[brids[i]] = brid_block_starts[i]
                        tail_block_starts[trids[i]] = trid_block_starts[i]
                else:
                    break

        return keys, base_block_starts, tail_block_starts

    def write_key_directory_set(self, keys, base_block_starts, tail_block_starts):
        data = bytearray(0)
        k = list(keys.keys())
        brids = list(keys.values())
        brid_block_starts = list(base_block_starts.values())
        trids = list(tail_block_starts.keys())
        trid_block_starts = list(tail_block_starts.values())

        k_bytes = []
        brids_bytes = []
        brid_block_starts_bytes = []
        trids_bytes = []
        trid_block_starts_bytes = []

        # convert 64 bit integers into bytes
        for num in k:
            for byte in int.to_bytes(num, length=8, byteorder="little"):
                k_bytes.append(byte)

        for num in brids:
            for byte in int.to_bytes(num, length=8, byteorder="little"):
                brids_bytes.append(byte)

        for num in trids:
            for byte in int.to_bytes(num, length=8, byteorder="little"):
                trids_bytes.append(byte)

        for num in brid_block_starts:
            for byte in int.to_bytes(num, length=8, byteorder="little"):
                brid_block_starts_bytes.append(byte)

        for num in trid_block_starts:
            for byte in int.to_bytes(num, length=8, byteorder="little"):
                trid_block_starts_bytes.append(byte)

        # append bytes to data properly
        key_directory_sets_count = math.ceil((len(k) // RECORDS_PER_PAGE) + 1) if \
            (len(k) // RECORDS_PER_PAGE) < (len(k) / RECORDS_PER_PAGE) else (len(k) // RECORDS_PER_PAGE)
        for i in range(key_directory_sets_count):
            bytes = bytearray(k_bytes[(PAGE_SIZE * i):(PAGE_SIZE * i) + PAGE_SIZE])
            pad_byte_array(bytes)
            data.extend(bytearray(bytes))

            bytes = bytearray(brids_bytes[(PAGE_SIZE * i):(PAGE_SIZE * i) + PAGE_SIZE])
            pad_byte_array(bytes)
            data.extend(bytearray(bytes))

            bytes = bytearray(trids_bytes[(PAGE_SIZE * i):(PAGE_SIZE * i) + PAGE_SIZE])
            pad_byte_array(bytes)
            data.extend(bytearray(bytes))

            bytes = bytearray(brid_block_starts_bytes[(PAGE_SIZE * i):(PAGE_SIZE * i) + PAGE_SIZE])
            pad_byte_array(bytes)
            data.extend(bytearray(bytes))

            bytes = bytearray(trid_block_starts_bytes[(PAGE_SIZE * i):(PAGE_SIZE * i) + PAGE_SIZE])
            pad_byte_array(bytes)
            data.extend(bytearray(bytes))

        # rewrite key directory file with new key directory data
        with open(self.key_directory, "wb") as f:
            f.write(data)

    def read_base_page_set(self, block_start_index):
        page_set = PageSet(self.num_columns + META_DATA_PAGES)
        with open(self.base_fn, "rb") as f:
            f.seek(block_start_index * PAGE_SIZE)
            for i in range(self.num_columns + META_DATA_PAGES):
                page_set.pages[i] = f.read(PAGE_SIZE)

        return page_set

    def write_base_page_set(self, page_set, block_start_index):
        with open(self.base_fn, "ab") as f:
            f.seek(block_start_index * PAGE_SIZE)
            for i in range(self.num_columns + META_DATA_PAGES):
                f.write(page_set.pages[i].data)

    def read_tail_page_set(self, block_start_index):
        page_set = PageSet(self.num_columns + META_DATA_PAGES)
        with open(self.tail_fn, "rb") as f:
            f.seek(block_start_index * PAGE_SIZE)
            for i in range(self.num_columns + META_DATA_PAGES):
                page_set.pages[i] = f.read(PAGE_SIZE)

        return page_set

    def write_tail_page_set(self, page_set, block_start_index):
        with open(self.tail_fn, "ab") as f:
            f.seek(block_start_index * PAGE_SIZE)
            for i in range(self.num_columns + META_DATA_PAGES):
                f.write(page_set.pages[i].data)

    def get_next_tail_block(self):
        block_num = self.next_tail_block
        self.next_tail_block += 1
        return block_num
