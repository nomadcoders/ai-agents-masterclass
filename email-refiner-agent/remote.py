import vertexai
from vertexai import agent_engines

PROJECT_ID = "gen-lang-client-0125196626"
LOCATION = "europe-southwest1"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
)

# deployments = agent_engines.list()

# for deployment in deployments:
#     print(deployment)

DEPLOYMENT_ID = "projects/23382131925/locations/europe-southwest1/reasoningEngines/2153529862441140224"

SESSION_ID = "5724511082748313600"

remote_app = agent_engines.get(DEPLOYMENT_ID)

remote_app.delete(force=True)


# # remote_session = remote_app.create_session(user_id="u_123")

# # print(remote_session["id"])

# for event in remote_app.stream_query(
#     user_id="u_123",
#     session_id=SESSION_ID,
#     message="I'm going to Laos, any tips?",
# ):
#     print(event, "\n", "=" * 50)
