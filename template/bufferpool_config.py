START_RID = 0
PAGE_SETS = 16
PAGE_SIZE = 4096
RECORDS_PER_PAGE = PAGE_SIZE // 8
#BUFFERPOOL_SIZE = 1073741824  # 1GB buffer pool size
BUFFERPOOL_SIZE = 1048576
META_DATA_PAGES = 5
PAGES_PER_KEY_DIRECTORY_SET = 5
KEY_DIRECTORY_SET_SIZE = PAGES_PER_KEY_DIRECTORY_SET * PAGE_SIZE
MAX_PAGES_IN_BUFFER = BUFFERPOOL_SIZE // PAGE_SIZE
BASE_RID_TYPE = 0
TAIL_RID_TYPE = 1