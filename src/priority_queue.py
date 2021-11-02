# https://codereview.stackexchange.com/questions/225030/updateable-priority-queue
import heapq

class UpdateableQueue:
    """An updateable priority queue class"""
    def __init__(self, iterable=None):
        self._heap = []
        self._entry_finder = {}
        if iterable:
            for item in iterable:
                self._entry_finder[item[0]] = item[1]
                heapq.heappush(self._heap, (item[1], item[0]))

    def __getitem__(self, key):
        """
        Returns the item with the specified key, if exists. Else,
        it raises a `KeyError` exception
        """
        if key in self._entry_finder:
            return self._entry_finder[key]
        raise KeyError('Item not found in the priority queue')

    def __len__(self) -> int:
        """Returns the length of the queue """
        return len(self._entry_finder)

    def __contains__(self, key) -> bool:
        """Returns a boolean based on if the key is in the queue"""
        return key in self._entry_finder
    
    def has(self, key) -> bool:
        """Returns a boolean based on if the key is in the queue"""
        # User-facing wrapper for __contains__
        return self.__contains__(key)

    def update(self, key, priority):
        """
        Updates the priority of a given key. 
        If the key is not in the queue, a `KeyError` exception is raised.
        """
        if key in self._entry_finder:
            self.push(key, priority)
        else:
            raise KeyError('Item not found in the priority queue')

    def push(self, key, priority):
        """Pushses a priority into the queue"""
        self._entry_finder[key] = priority
        heapq.heappush(self._heap, (priority, key))

    def pop(self) -> tuple:
        """Removes a priority from the queue"""
        if not self._heap:
            raise IndexError("The heap is empty")

        value, key = self._heap[0]
        while key not in self or self._entry_finder[key] != value:
            heapq.heappop(self._heap)
            if not self._heap:
                raise IndexError("The heap is empty")
            value, key = self._heap[0]

        value, key = heapq.heappop(self._heap)
        del self._entry_finder[key]
        return key, value