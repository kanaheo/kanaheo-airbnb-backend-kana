import strawberry
from rooms import schema as rooms_schema

@strawberry.type
class Mutation:
    pass

@strawberry.type
class Query(rooms_schema.Query):
    pass

schema = strawberry.Schema(
    query=Query,
    # mutation=Mutation
)