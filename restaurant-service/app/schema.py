import strawberry
from typing import List, Optional
from .database import SessionLocal
from .models import Restaurant, MenuItem

@strawberry.type
class MenuType:
    id: int
    name: str
    description: Optional[str]
    price: float
    image_url: Optional[str]
    is_available: bool
    category: Optional[str]
    stock: int

@strawberry.type
class RestaurantType:
    id: int
    name: str
    address: str
    cuisine_type: str
    is_open: bool
    image_url: Optional[str]
    
    @strawberry.field
    def menus(self) -> List[MenuType]:
        db = SessionLocal()
        try:
            menus = db.query(MenuItem).filter(MenuItem.restaurant_id == self.id).all()
            return [
                MenuType(
                    id=m.id, name=m.name, description=m.description, 
                    price=float(m.price), image_url=m.image_url, is_available=bool(m.is_available),
                    category=m.category, stock=m.stock
                ) for m in menus
            ]
        finally:
            db.close()

@strawberry.type
class Query:
    @strawberry.field
    def restaurants(self) -> List[RestaurantType]:
        db = SessionLocal()
        try:
            restaurants = db.query(Restaurant).all()
            return [
                RestaurantType(
                    id=r.id, name=r.name, address=r.address, 
                    cuisine_type=r.cuisine_type, is_open=bool(r.is_open), image_url=r.image_url
                ) for r in restaurants
            ]
        finally:
            db.close()

    @strawberry.field(name="restaurantById")
    def restaurant_by_id(self, id: int) -> Optional[RestaurantType]:
        db = SessionLocal()
        try:
            r = db.query(Restaurant).filter(Restaurant.id == id).first()
            if r:
                return RestaurantType(
                    id=r.id, name=r.name, address=r.address, 
                    cuisine_type=r.cuisine_type, is_open=bool(r.is_open), image_url=r.image_url
                )
        finally:
            db.close()
        return None

    @strawberry.field
    def restaurant(self, id: int) -> Optional[RestaurantType]:
        db = SessionLocal()
        try:
            r = db.query(Restaurant).filter(Restaurant.id == id).first()
            if r:
                return RestaurantType(
                    id=r.id, name=r.name, address=r.address, 
                    cuisine_type=r.cuisine_type, is_open=bool(r.is_open), image_url=r.image_url
                )
        finally:
            db.close()
        return None

    @strawberry.field(name="allMenuItems")
    def all_menu_items(self) -> List[MenuType]:
        db = SessionLocal()
        try:
            items = db.query(MenuItem).all()
            return [
                MenuType(
                    id=m.id, name=m.name, description=m.description,
                    price=float(m.price), image_url=m.image_url, is_available=bool(m.is_available),
                    category=m.category, stock=m.stock
                ) for m in items
            ]
        finally:
            db.close()

    @strawberry.field
    def menu_items(self, restaurant_id: Optional[int] = None) -> List[MenuType]:
        db = SessionLocal()
        try:
            query = db.query(MenuItem)
            if restaurant_id:
                query = query.filter(MenuItem.restaurant_id == restaurant_id)
            items = query.all()
            return [
                MenuType(
                    id=m.id, name=m.name, description=m.description,
                    price=float(m.price), image_url=m.image_url, is_available=bool(m.is_available),
                    category=m.category, stock=m.stock
                ) for m in items
            ]
        finally:
            db.close()

@strawberry.type
class Mutation:
    @strawberry.mutation(name="createRestaurant")
    def create_restaurant(self, name: str, address: str, phone: str, description: Optional[str] = None) -> Optional[RestaurantType]:
        db = SessionLocal()
        try:
            restaurant = Restaurant(
                name=name,
                address=address,
                phone=phone,
                description=description
            )
            db.add(restaurant)
            db.commit()
            db.refresh(restaurant)
            return RestaurantType(
                id=restaurant.id, name=restaurant.name, address=restaurant.address,
                phone=restaurant.phone, description=restaurant.description
            )
        finally:
            db.close()
        return None

    @strawberry.mutation(name="createMenuItem")
    def create_menu_item(self, restaurant_id: int, name: str, description: Optional[str], price: float, category: str, stock: int = 0) -> Optional[MenuType]:
        db = SessionLocal()
        try:
            menu_item = MenuItem(
                restaurant_id=restaurant_id,
                name=name,
                description=description,
                price=price,
                category=category,
                stock=stock,
                is_available=True
            )
            db.add(menu_item)
            db.commit()
            db.refresh(menu_item)
            return MenuType(
                id=menu_item.id, name=menu_item.name, description=menu_item.description,
                price=float(menu_item.price), image_url=menu_item.image_url, is_available=bool(menu_item.is_available),
                category=menu_item.category, stock=menu_item.stock
            )
        finally:
            db.close()
        return None

    @strawberry.mutation
    def update_menu_availability(self, menu_id: int, is_available: bool) -> Optional[MenuType]:
        db = SessionLocal()
        try:
            menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
            if menu:
                menu.is_available = is_available
                db.commit()
                return MenuType(
                    id=menu.id, name=menu.name, description=menu.description,
                    price=float(menu.price), image_url=menu.image_url, is_available=bool(menu.is_available),
                    category=menu.category, stock=menu.stock
                )
        finally:
            db.close()
        return None

    @strawberry.mutation
    def update_menu_stock(self, menu_id: int, stock: int) -> Optional[MenuType]:
        db = SessionLocal()
        try:
            menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
            if menu:
                menu.stock = stock
                db.commit()
                return MenuType(
                    id=menu.id, name=menu.name, description=menu.description,
                    price=float(menu.price), image_url=menu.image_url, is_available=bool(menu.is_available),
                    category=menu.category, stock=menu.stock
                )
        finally:
            db.close()
        return None

schema = strawberry.Schema(query=Query, mutation=Mutation)