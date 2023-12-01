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

        def __init__(self, right_fork, left_philosopher=None):
            right_fork: CircleTable.__Fork = right_fork
            left_philosopher: CircleTable.__Philosopher = left_philosopher

            self.state = self.__PhilosopherState.PONDERS

            if left_philosopher is None:
                self.__number: int = 1

                self.right_philosopher = self
                self.left_fork = right_fork
                self.right_fork = right_fork
            else:
                self.__number: int = left_philosopher.get_number() + 1

                self.right_philosopher = \
                    left_philosopher.right_philosopher
                self.left_fork = left_philosopher.right_fork
                self.right_fork = right_fork

                self.right_philosopher.left_fork = right_fork
                left_philosopher.right_philosopher = self

        def get_number(self) -> int:
            return self.__number

        def start_meals(self) -> None:
            while True:
                match self.state:
                    case self.__PhilosopherState.PONDERS:

                        time_to_ponders = random.uniform(1, 10)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.get_number(),
                            self.state.value,
                            time_to_ponders)
                        time.sleep(time_to_ponders)

                        self.state = self.__PhilosopherState.TAKES_LEFT_FORK
                    case self.__PhilosopherState.TAKES_LEFT_FORK:

                        self.left_fork.lock.acquire()

                        time_to_take_left = random.uniform(2, 4)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.get_number(),
                            self.state.value,
                            time_to_take_left)
                        time.sleep(time_to_take_left)

                        self.state = self.__PhilosopherState.TAKES_RIGHT_FORK
                    case self.__PhilosopherState.PUTS_LEFT_FORK:
                        time_to_put_left = random.uniform(1, 2)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.get_number(),
                            self.state.value,
                            time_to_put_left)
                        time.sleep(time_to_put_left)

                        self.left_fork.lock.release()

                        self.state = self.__PhilosopherState.PONDERS
                    case self.__PhilosopherState.TAKES_RIGHT_FORK:

                        if self.right_fork.lock.locked():
                            if (self.right_philosopher.state ==
                                    self.__PhilosopherState.TAKES_RIGHT_FORK):
                                self.right_philosopher.state = \
                                    self.__PhilosopherState.PUTS_LEFT_FORK
                            continue

                        self.right_fork.lock.acquire()

                        time_to_take_right = random.uniform(2, 4)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.get_number(),
                            self.state.value,
                            time_to_take_right)
                        time.sleep(time_to_take_right)

                        self.state = self.__PhilosopherState.EATING
                    case self.__PhilosopherState.EATING:

                        time_to_eating = random.uniform(5, 10)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.get_number(),
                            self.state.value,
                            time_to_eating)
                        time.sleep(time_to_eating)

                        self.state = \
                            self.__PhilosopherState.PUTS_FORKS_IN_PLACE
                    case self.__PhilosopherState.PUTS_FORKS_IN_PLACE:

                        time_to_put = random.uniform(1, 2)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.get_number(),
                            self.state.value,
                            time_to_put)
                        time.sleep(time_to_put)

                        self.left_fork.lock.release()
                        self.right_fork.lock.release()

                        self.state = self.__PhilosopherState.CHILLING
                    case self.__PhilosopherState.CHILLING:
                        return

    def __init__(self):
        self.__last_philosopher: CircleTable.__Philosopher | None = None

    def add_philosopher(self) -> None:
        self.__last_philosopher = self.__Philosopher(
            self.__Fork(), self.__last_philosopher)

    def start_meals(self, log_dataframe: DataFrame | None = None) -> None:
        if self.__last_philosopher is None:
            return

        threads: set[threading.Thread] = set()

        ph = self.__last_philosopher
        while True:
            ph = ph.right_philosopher
            threads.add(threading.Thread(target=ph.start_meals))
            if ph == self.__last_philosopher:
                break

        for th in threads:
            th.start()

        if log_dataframe is not None:
            while True:
                statuses: list[str] = []

                ph = self.__last_philosopher
                while True:
                    ph = ph.right_philosopher
                    statuses.append(ph.state.value.strip())
                    if ph == self.__last_philosopher:
                        break

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
