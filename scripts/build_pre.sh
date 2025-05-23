IMAGE_TAG_VER="1.0.0a001"
IMAGE_TAG="momoyeyu/pingpongbuddy"
IMAGE_HUB="harbor.lab.bigai.site"
IMAGE_HUB_USER=${IMAGE_HUB_USER}
IMAGE_HUB_PASS=${IMAGE_HUB_PASS}
IMAGE_SRC_PATH="./"

docker build -t $IMAGE_HUB/$IMAGE_TAG:$IMAGE_TAG_VER -t $IMAGE_HUB/$IMAGE_TAG:latest $IMAGE_SRC_PATH

docker build -f Dockerfile.pre -t harbor.lab.bigai.site/momoyeyu/pingpongbuddy:$IMAGE_TAG_VER -t harbor.lab.bigai.site/momoyeyu/pingpongbuddy:latest ./
