package test;
import java.io.IOException;
import java.net.ServerSocket;
import java.util.HashMap;
import java.util.UUID;

public class SocketConnector {

    ServerSocket server;
    int port;
    HashMap<UUID, Connection> connections;
    boolean running;

    public SocketConnector(int port) {

        this.port = port;
        this.connections = new HashMap<>();

        try {

            this.server = new ServerSocket(port);

        } catch (IOException e) {

            throw new RuntimeException(e);

        }
    }

    public void start_connector() throws IOException {

        running = true;

        while (running) {

            Connection newConnection = new Connection(port, server.accept());
            connections.put(newConnection.uuid, newConnection);
        }
    }

    public String sendMessage(String message, UUID uuid) throws IOException {

        Connection connection =  connections.get(uuid);
        connection.sendCommand(message);
        return connection.receiveResponse();
    }

    public void stop() throws IOException {

        running = false;
        server.close();


    }
}


