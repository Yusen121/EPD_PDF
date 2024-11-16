import time


class SnowflakeIDGenerator:
    def __init__(self, datacenter_id, worker_id, sequence=0):
        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = sequence
        self.datacenter_id_bits = 5
        self.worker_id_bits = 5
        self.sequence_bits = 12
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)
        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits
        self.epoch = 1288834974657  # Twitter的雪花算法纪元开始时间戳（毫秒）
        self.last_timestamp = -1

        if self.worker_id > self.max_worker_id or self.worker_id < 0:
            raise ValueError(f"Worker ID can't be greater than {self.max_worker_id} or less than 0")
        if self.datacenter_id > self.max_datacenter_id or self.datacenter_id < 0:
            raise ValueError(f"Datacenter ID can't be greater than {self.max_datacenter_id} or less than 0")

    def _time_gen(self):
        return int(time.time() * 1000)

    def _till_next_millis(self, last_timestamp):
        timestamp = self._time_gen()
        while timestamp <= last_timestamp:
            timestamp = self._time_gen()
        return timestamp

    def next_id(self):
        timestamp = self._time_gen()

        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards. Refusing to generate id")

        if self.last_timestamp == timestamp:
            self.sequence = (self.sequence + 1) & self.sequence_mask
            if self.sequence == 0:
                timestamp = self._till_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        new_id = ((timestamp - self.epoch) << self.timestamp_left_shift) | \
                 (self.datacenter_id << self.datacenter_id_shift) | \
                 (self.worker_id << self.worker_id_shift) | self.sequence

        return new_id
