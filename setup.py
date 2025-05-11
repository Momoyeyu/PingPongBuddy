from setuptools import setup, find_packages

setup(
    name="pingpongbuddy",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "langchain",
        "langchain-openai",
        "langchain-core",
        "psycopg2-binary",
        "streamlit",
        "python-dotenv",
        "fastapi",
        "uvicorn[standard]",
        "pydantic"
    ],
    author="PingPongBuddy Team",
    author_email="example@example.com",
    description="乒乓球约球智能助手",
    keywords="pingpong, ai, langchain",
    url="https://pingpongbuddy.example.com",
) 