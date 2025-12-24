import strawberry
from typing import List, Optional
from .database import SessionLocal
from .models import Driver, DeliveryTask, DriverSalary

@strawberry.type
class DriverType:
    id: int
    user_id: int
    vehicle_type: str
    vehicle_number: str
    is_available: bool
    is_on_job: bool
    total_earnings: float

    # snake_case fields (expose alongside camelCase)
    @strawberry.field(name="user_id")
    def user_id(self) -> int:
        return self.__dict__.get('user_id')

    @strawberry.field(name="vehicle_type")
    def vehicle_type(self) -> str:
        return self.__dict__.get('vehicle_type')

    @strawberry.field(name="vehicle_number")
    def vehicle_number(self) -> str:
        return self.__dict__.get('vehicle_number')

    @strawberry.field(name="is_available")
    def is_available(self) -> bool:
        return bool(self.__dict__.get('is_available'))

    @strawberry.field(name="is_on_job")
    def is_on_job(self) -> bool:
        return bool(self.__dict__.get('is_on_job'))

    @strawberry.field(name="total_earnings")
    def total_earnings(self) -> float:
        return float(self.__dict__.get('total_earnings') or 0.0)

    # camelCase aliases for compatibility with clients/Postman
    @strawberry.field(name="userId")
    def userId(self) -> int:
        return self.__dict__.get('user_id')

    @strawberry.field(name="vehicleType")
    def vehicleType(self) -> str:
        return self.__dict__.get('vehicle_type')

    @strawberry.field(name="vehicleNumber")
    def vehicleNumber(self) -> str:
        return self.__dict__.get('vehicle_number')

    @strawberry.field(name="isAvailable")
    def isAvailable(self) -> bool:
        return bool(self.__dict__.get('is_available'))

    @strawberry.field(name="isOnJob")
    def isOnJob(self) -> bool:
        return bool(self.__dict__.get('is_on_job'))

    @strawberry.field(name="totalEarnings")
    def totalEarnings(self) -> float:
        return float(self.__dict__.get('total_earnings') or 0.0)

@strawberry.type
class DeliveryTaskType:
    id: int
    order_id: int
    driver_id: int
    status: str

    # snake_case fields
    @strawberry.field(name="order_id")
    def order_id(self) -> int:
        return self.__dict__.get('order_id')

    @strawberry.field(name="driver_id")
    def driver_id(self) -> int:
        return self.__dict__.get('driver_id')

    # camelCase aliases
    @strawberry.field(name="orderId")
    def orderId(self) -> int:
        return self.__dict__.get('order_id')

    @strawberry.field(name="driverId")
    def driverId(self) -> int:
        return self.__dict__.get('driver_id')

@strawberry.type
class Query:
    @strawberry.field(name="drivers")
    def all_drivers(self) -> List["DriverGQL"]:
        db = SessionLocal()
        try:
            drivers = db.query(Driver).all()
            return [
                DriverGQL(
                    id=d.id,
                    userId=d.user_id,
                    vehicleType=d.vehicle_type,
                    vehicleNumber=d.vehicle_number,
                    isAvailable=bool(d.is_available),
                    isOnJob=bool(d.is_on_job),
                    totalEarnings=float(d.total_earnings)
                ) for d in drivers
            ]
        finally:
            db.close()

    @strawberry.field(name="driverById")
    def driver_by_id(self, id: int) -> Optional["DriverGQL"]:
        db = SessionLocal()
        try:
            driver = db.query(Driver).filter(Driver.id == id).first()
            if driver:
                return DriverGQL(
                    id=driver.id,
                    userId=driver.user_id,
                    vehicleType=driver.vehicle_type,
                    vehicleNumber=driver.vehicle_number,
                    isAvailable=bool(driver.is_available),
                    isOnJob=bool(driver.is_on_job),
                    totalEarnings=float(driver.total_earnings)
                )
        finally:
            db.close()
        return None

    @strawberry.field(name="availableDrivers")
    def available_drivers(self) -> List["DriverGQL"]:
        db = SessionLocal()
        try:
            drivers = db.query(Driver).filter(Driver.is_available == True).all()
            return [
                DriverGQL(
                    id=d.id,
                    userId=d.user_id,
                    vehicleType=d.vehicle_type,
                    vehicleNumber=d.vehicle_number,
                    isAvailable=bool(d.is_available),
                    isOnJob=bool(d.is_on_job),
                    totalEarnings=float(d.total_earnings)
                ) for d in drivers
            ]
        finally:
            db.close()

    @strawberry.field(name="driverDeliveries")
    def driver_deliveries(self, driver_id: int) -> List["DeliveryTaskGQL"]:
        db = SessionLocal()
        try:
            tasks = db.query(DeliveryTask).filter(DeliveryTask.driver_id == driver_id).all()
            return [
                DeliveryTaskGQL(
                    id=t.id,
                    orderId=t.order_id,
                    driverId=t.driver_id,
                    status=t.status
                ) for t in tasks
            ]
        finally:
            db.close()

    @strawberry.field
    def delivery_tasks(self, driver_id: Optional[int] = None) -> List[DeliveryTaskType]:
        db = SessionLocal()
        try:
            query = db.query(DeliveryTask)
            if driver_id:
                query = query.filter(DeliveryTask.driver_id == driver_id)
            tasks = query.all()
            return [
                DeliveryTaskType(
                    id=t.id,
                    order_id=t.order_id,
                    driver_id=t.driver_id,
                    status=t.status
                ) for t in tasks
            ]
        finally:
            db.close()

    # Snake_case-compatible queries (return types with snake_case fields)
    @strawberry.field(name="drivers_snake")
    def drivers_snake(self) -> List["DriverTypeSnake"]:
        db = SessionLocal()
        try:
            drivers = db.query(Driver).all()
            return [
                DriverTypeSnake(
                    id=d.id,
                    user_id=d.user_id,
                    vehicle_type=d.vehicle_type,
                    vehicle_number=d.vehicle_number,
                    is_available=bool(d.is_available),
                    is_on_job=bool(d.is_on_job),
                    total_earnings=float(d.total_earnings)
                ) for d in drivers
            ]
        finally:
            db.close()

    @strawberry.field(name="driver_by_id_snake")
    def driver_by_id_snake(self, id: int) -> Optional["DriverTypeSnake"]:
        db = SessionLocal()
        try:
            driver = db.query(Driver).filter(Driver.id == id).first()
            if driver:
                return DriverTypeSnake(
                    id=driver.id,
                    user_id=driver.user_id,
                    vehicle_type=driver.vehicle_type,
                    vehicle_number=driver.vehicle_number,
                    is_available=bool(driver.is_available),
                    is_on_job=bool(driver.is_on_job),
                    total_earnings=float(driver.total_earnings)
                )
        finally:
            db.close()
        return None

@strawberry.type
class Mutation:
    @strawberry.mutation(name="createDriver")
    def create_driver(self, user_id: int, vehicle_type: str, vehicle_number: str) -> Optional["DriverGQL"]:
        db = SessionLocal()
        try:
            driver = Driver(
                user_id=user_id,
                vehicle_type=vehicle_type,
                vehicle_number=vehicle_number,
                is_available=True,
                is_on_job=False,
                total_earnings=0.0
            )
            db.add(driver)
            db.commit()
            db.refresh(driver)
            return DriverGQL(
                id=driver.id,
                userId=driver.user_id,
                vehicleType=driver.vehicle_type,
                vehicleNumber=driver.vehicle_number,
                isAvailable=bool(driver.is_available),
                isOnJob=bool(driver.is_on_job),
                totalEarnings=float(driver.total_earnings)
            )
        finally:
            db.close()
        return None

    @strawberry.mutation(name="updateDriverStatus")
    def update_driver_status(self, driver_id: int, is_available: bool, is_on_job: bool) -> Optional["DriverGQL"]:
        db = SessionLocal()
        try:
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if driver:
                driver.is_available = is_available
                driver.is_on_job = is_on_job
                db.commit()
                
                return DriverGQL(
                    id=driver.id,
                    userId=driver.user_id,
                    vehicleType=driver.vehicle_type,
                    vehicleNumber=driver.vehicle_number,
                    isAvailable=bool(driver.is_available),
                    isOnJob=bool(driver.is_on_job),
                    totalEarnings=float(driver.total_earnings)
                )
        finally:
            db.close()
        return None

    @strawberry.mutation(name="createDelivery")
    def create_delivery(self, order_id: int, driver_id: int) -> Optional[DeliveryTaskType]:
        db = SessionLocal()
        try:
            task = DeliveryTask(order_id=order_id, driver_id=driver_id, status="ASSIGNED")
            db.add(task)
            
            # Update driver status
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if driver:
                driver.is_on_job = True
            
            db.commit()
            db.refresh(task)
            return DeliveryTaskType(
                id=task.id,
                order_id=task.order_id,
                driver_id=task.driver_id,
                status=task.status
            )
        finally:
            db.close()
        return None

    @strawberry.mutation
    def assign_driver(self, order_id: int) -> Optional[DriverType]:
        db = SessionLocal()
        try:
            # Cari driver yang tersedia dan tidak sedang mengerjakan
            driver = db.query(Driver).filter(
                Driver.is_available == True,
                Driver.is_on_job == False
            ).first()
            
            if driver:
                # Buat delivery task
                task = DeliveryTask(order_id=order_id, driver_id=driver.id, status="ASSIGNED")
                db.add(task)
                
                # Update driver status
                driver.is_on_job = True
                db.commit()
                
                return DriverType(
                    id=driver.id,
                    user_id=driver.user_id,
                    vehicle_type=driver.vehicle_type,
                    vehicle_number=driver.vehicle_number,
                    is_available=bool(driver.is_available),
                    is_on_job=bool(driver.is_on_job),
                    total_earnings=float(driver.total_earnings)
                )
        finally:
            db.close()
        return None

# delay schema creation until all types (including snake_case types) are defined


@strawberry.type
class DriverTypeSnake:
    id: int
    user_id: int
    vehicle_type: str
    vehicle_number: str
    is_available: bool
    is_on_job: bool
    total_earnings: float


@strawberry.type
class DeliveryTaskTypeSnake:
    id: int
    order_id: int
    driver_id: int
    status: str


@strawberry.type
class DriverGQL:
    id: int
    userId: int
    vehicleType: str
    vehicleNumber: str
    isAvailable: bool
    isOnJob: bool
    totalEarnings: float


@strawberry.type
class DeliveryTaskGQL:
    id: int
    orderId: int
    driverId: int
    status: str


schema = strawberry.Schema(query=Query, mutation=Mutation)
