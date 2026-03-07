from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter

likes_db = []
counter = 1


@strawberry.type
class Like:
    id: int
    target: str


@strawberry.type
class Query:
    @strawberry.field
    def likes(self) -> list[Like]:
        return likes_db

    @strawberry.field
    def like(self, id: int) -> Like | None:
        for like in likes_db:
            if like.id == id:
                return like
        return None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def createLike(self, target: str) -> Like:
        global counter
        like = Like(id=counter, target=target)
        likes_db.append(like)
        counter += 1
        return like


schema = strawberry.Schema(query=Query, mutation=Mutation)

app = FastAPI()
graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")