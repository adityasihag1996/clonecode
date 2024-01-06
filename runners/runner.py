import time
from redis import Redis
from rq import Worker, Queue, Connection
from multiprocessing import Process

from DockerManager import DockerManager

def start_worker():
    # RQ
    redis_rq_conn = Redis(
        host = '192.168.1.6',
        port = 4567,
        db = 0,
        password = 'yourpassword'
    )
    redis_rq = Queue('runs', connection = redis_rq_conn)

    with Connection(redis_rq_conn):
        worker = Worker([redis_rq])
        worker.work()

if __name__ == '__main__':
    parallels = 8

    # local Redis
    local_redis = Redis(
        host = 'localhost',
        port = 8899,
        db = 0,
        # password = 'yourpassword',
        decode_responses = True,
    )

    docker_manager = DockerManager()

    # create containers
    docker_containers = docker_manager.createContainers(num_containers = parallels)

    # store the contianer ids in local redis
    for container in docker_containers:
        # local_redis.zadd('containers', {container.id: 0})
        local_redis.getset(f"{container.id}", "false")
        
    # create and start worker processes
    processes = []
    for _ in range(parallels):
        process = Process(target=start_worker)
        process.start()
        processes.append(process)

    # Optionally, join the processes (not typically needed in a server context)
    for process in processes:
        process.join()

    
