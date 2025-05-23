IMAGE_TAG_VER="1.0.0a001"
IMAGE_TAG="junjie-su/pingpongbuddy"
IMAGE_HUB="harbor.lab.bigai.site"
IMAGE_HUB_USER=${IMAGE_HUB_USER}
IMAGE_HUB_PASS=${IMAGE_HUB_PASS}
IMAGE_SRC_PATH="./"
docker build -f pingpongbuddy/docker/Dockerfile -t $IMAGE_HUB/$IMAGE_TAG:$IMAGE_TAG_VER -t $IMAGE_HUB/$IMAGE_TAG:latest $IMAGE_SRC_PATH

docker build -f pingpongbuddy/docker/Dockerfile.pre -t harbor.lab.bigai.site/junjie-su/pingpongbuddy:$IMAGE_TAG_VER -t harbor.lab.bigai.site/junjie-su/pingpongbuddy:latest ./
