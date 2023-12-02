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
            PUTS_FORKS_IN_PLACE = 'puts forks in place\t'

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

        def start_meals(self, timeout) -> None:
            end_time = time.time() + timeout

            while time.time() < end_time:
                match self.state:
                    case self.__PhilosopherState.PONDERS:

                        time_to_ponders = random.uniform(1, 10)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.get_number(),
                            self.state.value,
                            time_to_ponders)
                        if time.time() + time_to_ponders >= end_time:
                            break
                        time.sleep(time_to_ponders)

                        self.state = self.__PhilosopherState.TAKES_LEFT_FORK
                    case self.__PhilosopherState.TAKES_LEFT_FORK:

                        if self.left_fork.lock.locked():
                            continue

                        self.left_fork.lock.acquire()

                        time_to_take_left = random.uniform(2, 4)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.get_number(),
                            self.state.value,
                            time_to_take_left)
                        if time.time() + time_to_take_left >= end_time:
                            break
                        time.sleep(time_to_take_left)

                        self.state = self.__PhilosopherState.TAKES_RIGHT_FORK
                    case self.__PhilosopherState.PUTS_LEFT_FORK:

                        time_to_put_left = random.uniform(1, 2)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.get_number(),
                            self.state.value,
                            time_to_put_left)
                        if time.time() + time_to_put_left >= end_time:
                            break
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
                        if time.time() + time_to_take_right >= end_time:
                            break
                        time.sleep(time_to_take_right)

                        self.state = self.__PhilosopherState.EATING
                    case self.__PhilosopherState.EATING:

                        time_to_eating = random.uniform(5, 10)
                        logging.debug(
                            '__Philosopher\t#%d\t%s in %f seconds',
                            self.get_number(),
                            self.state.value,
                            time_to_eating)
                        if time.time() + time_to_eating >= end_time:
                            break
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
                        if time.time() + time_to_put >= end_time:
                            break
                        time.sleep(time_to_put)

                        self.left_fork.lock.release()
                        self.right_fork.lock.release()

                        self.state = self.__PhilosopherState.PONDERS

            match self.state:
                case (self.__PhilosopherState.PUTS_LEFT_FORK |
                        self.__PhilosopherState.TAKES_RIGHT_FORK):
                    self.left_fork.lock.release()
                case (self.__PhilosopherState.EATING |
                        self.__PhilosopherState.PUTS_FORKS_IN_PLACE):
                    self.left_fork.lock.release()
                    self.right_fork.lock.release()

    def __init__(self):
        self.__last_philosopher: CircleTable.__Philosopher | None = None

    def add_philosopher(self) -> None:
        self.__last_philosopher = self.__Philosopher(
            self.__Fork(), self.__last_philosopher)

    def start_meals(
        self,
        timeout: int = 40,
        log_dataframe: DataFrame | None = None
    ) -> None:
        if self.__last_philosopher is None:
            return

        threads: set[threading.Thread] = set()

        ph = self.__last_philosopher
        while True:
            ph = ph.right_philosopher
            threads.add(threading.Thread(
                target=ph.start_meals, kwargs={'timeout': timeout}))
            if ph == self.__last_philosopher:
                break

        for th in threads:
            th.start()

        if log_dataframe is not None:
            current_time = 0

            while True:
                statuses: list[str] = []

                ph = self.__last_philosopher
                while True:
                    ph = ph.right_philosopher
                    statuses.append(ph.state.value.strip())
                    if ph == self.__last_philosopher:
                        break

                log_dataframe.loc[current_time] = statuses

                if all(not th.is_alive() for th in threads):
                    break

                current_time += 1
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

    table.start_meals(timeout=180, log_dataframe=log)

    print(log)
    log.to_excel("lab4/lad4.log.xlsx")
