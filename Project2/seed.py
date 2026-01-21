import random
from faker import Faker
from sqlalchemy import select, func
from core.database import SessionLocal
from core.security import hash_password
from models.user import User, UserRole
from models.tool import Tool
from models.review import Review

fake = Faker()


class DatabaseSeeder:
    async def seed_data(self):
        async with SessionLocal(expire_on_commit=False) as session:

            result = await session.execute(select(func.count(User.id)))
            if result.scalar() > 5:
                print("Database already has data. Skipping seed.")
                return

            print("Starting large scale seeding...")

            users = []
            admin = User(
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN
            )
            users.append(admin)

            for _ in range(2000):
                users.append(User(
                    email=fake.unique.email(),
                    hashed_password=hash_password("password123"),
                    role=UserRole.USER
                ))

            session.add_all(users)
            await session.flush()
            print(f"Generated {len(users)} users.")

            categories = ["Chat", "Image", "Video", "Coding", "Marketing", "Audio"]
            tools = []
            for _ in range(1500):
                tools.append(Tool(
                    name=fake.company() + " AI",
                    description=fake.catch_phrase() + ". " + fake.paragraph(nb_sentences=2),
                    url=fake.url(),
                    category=random.choice(categories),
                    avg_rating=0.0
                ))

            approval = [False, True]

            session.add_all(tools)
            await session.flush()
            print(f"Generated {len(tools)} tools.")

            reviews = []
            for _ in range(2000):
                random_user = random.choice(users)
                random_tool = random.choice(tools)

                reviews.append(Review(
                    user_id=random_user.id,
                    tool_id=random_tool.id,
                    rating=random.randint(3, 5),
                    comment=fake.sentence(nb_words=12),
                    approved=random.choice(approval)
                ))

            session.add_all(reviews)
            await session.commit()
            print(f"Generated {len(reviews)} reviews.")

            print("Calculating average ratings...")
            for tool in tools:
                tool_reviews = [r.rating for r in reviews if r.tool_id == tool.id and r.approved]
                if tool_reviews:
                    tool.avg_rating = round(sum(tool_reviews) / len(tool_reviews), 2)
                else:
                    tool.avg_rating = 0.0

            await session.commit()
            print("Database Seeding Complete!")