import threading
import time
import random
import logging

from dataclasses import dataclass, field
from enum import Enum
from pandas import DataFrame


class CircleTable:

    @dataclass
    class __Fork:
        class __Philosopher:
            ...
        left_philosopher: __Philosopher | None = None
        right_philosopher: __Philosopher | None = None
        lock: threading.Lock = field(default_factory=threading.Lock)

    class __Philosopher:

        class __PhilosopherState(Enum):
            PONDERS = 'ponders\t\t\t'
            TAKES_LEFT_FORK = 'takes left fork\t\t'
            PUTS_LEFT_FORK = 'puts left fork\t\t'
            TAKES_RIGHT_FORK = 'takes right fork\t'
            EATING = 'eating\t\t\t'
            PUTS_FORKS_IN_PLACE = 'puts forks in plase\t'
            CHILLING = 'chilling\t\t\t'

        def __init__(self):
            self.number = -1
            self.left_fork: CircleTable.__Fork | None = None
            self.right_fork: CircleTable.__Fork | None = None
            self.state = self.__PhilosopherState.PONDERS

        def start_meals(self):
            while True:
                match self.state:
                    case self.__PhilosopherState.PONDERS:
                        time_to_ponders = random.uniform(1, 10)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.number,
                            self.state.value,
                            time_to_ponders)
                        time.sleep(time_to_ponders)

                        self.state = self.__PhilosopherState.TAKES_LEFT_FORK
                    case self.__PhilosopherState.TAKES_LEFT_FORK:

                        self.left_fork.lock.acquire()

                        time_to_take_left = random.uniform(2, 4)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.number,
                            self.state.value,
                            time_to_take_left)
                        time.sleep(time_to_take_left)

                        self.state = self.__PhilosopherState.TAKES_RIGHT_FORK
                    case self.__PhilosopherState.PUTS_LEFT_FORK:
                        time_to_put_left = random.uniform(1, 2)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.number,
                            self.state.value,
                            time_to_put_left)
                        time.sleep(time_to_put_left)

                        self.left_fork.lock.release()

                        self.state = self.__PhilosopherState.PONDERS
                    case self.__PhilosopherState.TAKES_RIGHT_FORK:

                        if self.right_fork.lock.locked():
                            if (self.right_fork.right_philosopher.state ==
                                    self.__PhilosopherState.TAKES_RIGHT_FORK):
                                self.right_fork.right_philosopher.state = \
                                    self.__PhilosopherState.PUTS_LEFT_FORK
                            continue

                        self.right_fork.lock.acquire()

                        time_to_take_right = random.uniform(2, 4)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.number,
                            self.state.value,
                            time_to_take_right)
                        time.sleep(time_to_take_right)

                        self.state = self.__PhilosopherState.EATING
                    case self.__PhilosopherState.EATING:
                        time_to_eating = random.uniform(5, 10)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.number,
                            self.state.value,
                            time_to_eating)
                        time.sleep(time_to_eating)

                        self.state = \
                            self.__PhilosopherState.PUTS_FORKS_IN_PLACE
                    case self.__PhilosopherState.PUTS_FORKS_IN_PLACE:
                        time_to_put = random.uniform(1, 2)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.number,
                            self.state.value,
                            time_to_put)
                        time.sleep(time_to_put)

                        self.left_fork.lock.release()
                        self.right_fork.lock.release()

                        self.state = self.__PhilosopherState.CHILLING
                    case self.__PhilosopherState.CHILLING:
                        return

    def __init__(self):
        self.__philosophers: list[self.__Philosopher] = []
        self.__ph_dict: dict[int, self.__Philosopher] = {}
        self.__forks: list[self.__Fork] = []

    def add_philosopher(self):
        new_phil = self.__Philosopher()
        new_fork = self.__Fork()

        new_phil.right_fork = new_fork
        new_fork.left_philosopher = new_phil

        if len(self.__philosophers) == 0:
            new_phil.left_fork = new_fork
            new_fork.right_philosopher = new_phil

            self.__philosophers.append(new_phil)
            self.__forks.append(new_fork)
            return

        neighbor: self.__Philosopher = random.choice(self.__philosophers)

        self.__philosophers.append(new_phil)
        self.__forks.append(new_fork)

        new_phil.left_fork = neighbor.left_fork
        new_phil.left_fork.right_philosopher = new_phil

        neighbor.left_fork = new_fork
        new_fork.right_philosopher = neighbor

    def __count_off(self):
        phil: self.__Philosopher = random.choice(self.__philosophers)

        if phil.number != -1:
            return

        while phil.number != len(self.__philosophers):
            phil_num = phil.number
            phil = phil.right_fork.right_philosopher
            phil.number = phil_num + 1

            if phil.number > 0:
                self.__ph_dict[phil.number] = phil

    def start_meals(self, log_dataframe: DataFrame | None = None):
        self.__count_off()

        threads: threading.Thread = set()

        for ph in self.__philosophers:
            threads.add(threading.Thread(target=ph.start_meals))

        for th in threads:
            th.start()

        if log_dataframe is not None:
            while True:
                statuses = [
                    self.__ph_dict[i].state.value.strip()
                    for i in range(1, len(self.__philosophers) + 1)]

                if len(log_dataframe.index) > 0:
                    next_time_step = log_dataframe.index[-1] + 1
                else:
                    next_time_step = 0
                log_dataframe.loc[next_time_step] = statuses

                if all(not th.is_alive() for th in threads):
                    break
                time.sleep(1)

        for th in threads:
            th.join()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    table = CircleTable()

    N = 5

    for _ in range(N):
        table.add_philosopher()

    log = DataFrame(columns=[f'philosopher #{i}'
                             for i in range(1, N + 1)])
    log.index.name = 'time_slice'

    table.start_meals(log)

    print(log)
