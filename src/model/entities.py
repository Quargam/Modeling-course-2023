import abc
import dataclasses
import typing
import random

from .tile import Point, Direction


class BaseModelAgent(abc.ABC):
    pass


@dataclasses.dataclass(frozen=True)
class MailPackage:
    id: int
    type_mail: str
    message: str = dataclasses.field(default='')


class Robot(BaseModelAgent):
    def __init__(
        self,
        id: int,
        location_point: Point,
        direction: Point = Direction.UP,
        package_mail: typing.Optional[MailPackage] = None
    ) -> None:
        self.id = id
        self.location_point = location_point
        self.direction = direction
        self.package_mail = package_mail

    def forward(self) -> None:
        self.location_point += self.direction

    def backward(self) -> None:
        self.location_point -= self.direction

    def turn_left(self) -> None:
        self.direction = Point(self.direction.y * -1, self.direction.x)

    def right_left(self) -> None:
        self.direction = Point(self.direction.y, self.direction.x * -1)

    def stand_here(self) -> None:
        pass

    def take_package(self, mail: MailPackage) -> None:
        assert not self.package_mail, 'The robot has a package.'
        self.package_mail = mail

    def give_package(self) -> MailPackage:
        assert self.package_mail, 'The robot does not have a package.'
        mail = self.package_mail
        self.package_mail = None
        return mail


class PackageConveyor(BaseModelAgent):
    _global_id_mail = 0
    _types_mail: typing.Set[str] = set()

    def __init__(
        self,
        id_conveyor: int,
        location_point: Point,
        types_mail: typing.Collection[str],
        expectation: typing.Optional[typing.Collection[float]],
        out_point: typing.Optional[Point] = None,
    ) -> None:
        self.id_conveyor = id_conveyor
        self.location_point = location_point
        self.types_mail = types_mail
        self.expectation = expectation
        self.out_point = out_point

        self.__post_init__()

    def __post_init__(self) -> None:
        for type_mail in self.types_mail:
            if type_mail not in PackageConveyor._types_mail:
                PackageConveyor._types_mail.add(type_mail)

    def return_package_mail(self) -> MailPackage:
        expectation = self.expectation or [1 / len(PackageConveyor._types_mail)
                                           for _ in range(len(PackageConveyor._types_mail))]
        mail = MailPackage(PackageConveyor._global_id_mail, random.choices(self.types_mail, expectation)[0])
        PackageConveyor._global_id_mail += 1
        return mail


class PackageStorage(BaseModelAgent):
    _types_mail: typing.Set[str] = set()

    def __init__(self, id: int, location_point: Point, types_mail: typing.Collection[str]) -> None:
        self.id = id
        self.location_point = location_point
        self.types_mail = types_mail

        self.__post_init__()

    def __post_init__(self) -> None:
        for type_mail in self.types_mail:
            if type_mail not in PackageStorage._types_mail:
                PackageStorage._types_mail.add(type_mail)

    def run(self) -> None:
        pass
