START_RID = 0
PAGE_SETS = 16
PAGE_SIZE = 4096
RECORDS_PER_PAGE = PAGE_SIZE / 8
BUFFER_POOL_PAGES = 1000000000  # 1GB buffer pool size
META_DATA_PAGES = 3
PAGES_PER_KEY_DIRECTORY_SET = 5
KEY_DIRECTORY_SET_SIZE = PAGES_PER_KEY_DIRECTORY_SET * PAGE_SIZE

def init():
    pass
