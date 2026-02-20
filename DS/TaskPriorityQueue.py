# ============================================================
# Max-Heap Priority Queue — Built from Scratch
# NO heapq, NO sorted(), NO built-in DS
# Used for: Sorting employee tasks by priority (high → medium → low)
# ============================================================

PRIORITY_MAP = {
    "high": 2,
    "medium": 1,
    "low": 0,
}


class TaskPriorityQueue:
    """
    Manual Max-Heap built from scratch using a plain list.

    Heap Array rules:
        Parent  of node i  →  (i - 1) // 2
        Left child of i    →  2 * i + 1
        Right child of i   →  2 * i + 2

    Max-Heap rule:
        Every parent >= its children
        So root is always the HIGHEST priority task
    """

    def __init__(self):
        self._heap = []
        self._counter = 0

    def _swap(self, i, j):
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    def _is_higher(self, i, j):
        if self._heap[i][0] != self._heap[j][0]:
            return self._heap[i][0] > self._heap[j][0]
        return self._heap[i][1] < self._heap[j][1]

    def _sift_up(self, index):
        while index > 0:
            parent = (index - 1) // 2
            if self._is_higher(index, parent):
                self._swap(index, parent)
                index = parent
            else:
                break

    def _sift_down(self, index):
        size = len(self._heap)
        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            largest = index

            if left < size and self._is_higher(left, largest):
                largest = left

            if right < size and self._is_higher(right, largest):
                largest = right

            if largest != index:
                self._swap(index, largest)
                index = largest
            else:
                break

    def push(self, task):
        # ✅ Normalize priority — strip spaces, lowercase
        raw_priority = task.get("priority") or "low"
        priority_key = str(raw_priority).strip().lower()
        priority_val = PRIORITY_MAP.get(priority_key, 0)

        node = [priority_val, self._counter, task]
        self._heap.append(node)
        self._counter += 1
        self._sift_up(len(self._heap) - 1)

    def push_all(self, tasks):
        for task in tasks:
            self.push(task)

    def pop(self):
        if not self._heap:
            return None
        self._swap(0, len(self._heap) - 1)
        node = self._heap.pop()
        if self._heap:
            self._sift_down(0)
        return node[2]

    def get_all(self):
        import copy

        saved_heap = copy.deepcopy(self._heap)
        saved_counter = self._counter

        sorted_tasks = []
        while not self.is_empty():
            sorted_tasks.append(self.pop())

        self._heap = saved_heap
        self._counter = saved_counter

        return sorted_tasks

    def peek(self):
        if self._heap:
            return self._heap[0][2]
        return None

    def is_empty(self):
        return len(self._heap) == 0

    def size(self):
        return len(self._heap)
