# Running a Redis Server and Client with Podman

This tutorial uses an Alpine-based `Containerfile` to build a Redis image, start a Redis server, and test it using `redis-cli`.

## 1. Containerfile

Save the following as `Containerfile`:

```dockerfile
FROM alpine

# Install Redis server and client utilities
RUN apk add --no-cache redis

# Start Redis by default
CMD ["redis-server"]
```

The `gcc` package from the original example is not needed for this basic exercise, so it has been omitted.

## 2. Build the image

Run this command from the directory containing `Containerfile`:

```cmd
podman build -t my-redis .
```

## 3. Start the Redis server

```cmd
podman run -d --name redis-server my-redis
```

Verify the container is running and inspect its logs:

```cmd
podman ps
podman logs redis-server
```

Redis listens on port `6379` inside the container.

## 4. Connect using Redis CLI inside the server container

Because the image includes Redis client utilities, you can run `redis-cli` inside the running server container:

```cmd
podman exec -it redis-server redis-cli
```

You should see a prompt similar to:

```text
127.0.0.1:6379>
```

## 5. Practise simple Redis commands

Enter these commands at the Redis prompt:

| Command | Purpose |
|---|---|
| `PING` | Test connectivity |
| `SET name "Podman Workshop"` | Store a key-value pair |
| `GET name` | Retrieve a value |
| `SET count 10` | Store a number |
| `INCR count` | Increment the number |
| `GET count` | Read the updated number |
| `KEYS *` | List keys; use only for this small lab |
| `DEL name` | Delete a key |
| `INFO server` | Display server information |
| `EXIT` | Exit the client |

Example session:

```text
127.0.0.1:6379> PING
PONG

127.0.0.1:6379> SET name "Podman Workshop"
OK

127.0.0.1:6379> GET name
"Podman Workshop"

127.0.0.1:6379> SET count 10
OK

127.0.0.1:6379> INCR count
(integer) 11

127.0.0.1:6379> GET count
"11"

127.0.0.1:6379> EXIT
```

## 6. Optional: Use a separate client container

This exercise demonstrates communication between two containers.

### Step 6.1 — Remove the first server

Exit `redis-cli`, then run:

```cmd
podman rm -f redis-server
podman network create redis-net
```

### Step 6.2 — Start Redis on the dedicated network

```cmd
podman run -d --name redis-server --network redis-net my-redis redis-server --bind 0.0.0.0 --protected-mode no
```

**Security note:** This command disables Redis protected mode for a simple, isolated learning exercise. Do not use this configuration on an untrusted network or in production. Do not publish the Redis port publicly.

### Step 6.3 — Start a separate Redis client

```cmd
podman run --rm -it --network redis-net my-redis redis-cli -h redis-server
```

The client connects to the server using its container name, `redis-server`, through the `redis-net` network.

Test the connection and store a value:

```text
redis-server:6379> PING
PONG

redis-server:6379> SET course "Redis Basics"
OK

redis-server:6379> GET course
"Redis Basics"

redis-server:6379> EXIT
```

## 7. Clean up

Remove the server and the dedicated network:

```cmd
podman rm -f redis-server
podman network rm redis-net
```

The client container is automatically removed when it exits because it was started with `--rm`.

## 8. Key learning points

- `podman build` builds an image from a `Containerfile`.
- `podman run -d` starts a container in the background.
- `podman exec -it` runs an interactive command inside an existing container.
- `redis-cli` is the command-line client for Redis.
- A Podman network lets containers communicate by container name.
- `-p 6379:6379` is not required when only containers on the same Podman network need to access Redis. Publish a port only when host-side access is needed, and secure it appropriately.

## 9. Optional: Access Redis from the host

If you want to connect to Redis from a Redis client installed on the host, publish the port when starting the server:

```cmd
podman run -d --name redis-host -p 127.0.0.1:6379:6379 my-redis redis-server --bind 0.0.0.0 --protected-mode no
```

This example binds the published port to the host loopback interface, not all host interfaces. It disables protected mode for demonstration, so use it only in a trusted local lab. Remove it when finished:

```cmd
podman rm -f redis-host
```

For production, configure Redis authentication and appropriate network restrictions instead of disabling protected mode.
