import java.io.IOException;
import java.net.ServerSocket;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.UUID;

public class SocketConnector {

    ServerSocket server;
    int port;
    HashMap<UUID, FeederConnection> connections;
    boolean running;
    private Connection database;

    public SocketConnector(int port) {

        this.port = port;
        this.connections = new HashMap<>();

        try {

            this.server = new ServerSocket(port);

        } catch (IOException e) {

            throw new RuntimeException(e);

        }
    }

    public void start_connector(Connection database) throws IOException, SQLException {

        running = true;
        this.database = database;

        while (running) {

            FeederConnection newConnection = new FeederConnection(port, server.accept());
            addConnection(newConnection);
        }
    }

    public void addConnection(FeederConnection newConnection) throws SQLException {


        PreparedStatement myStmt = database.prepareStatement("SELECT * FROM feeder where uuid = ?");
        myStmt.setString(1, newConnection.uuid.toString());
        ResultSet rs = myStmt.executeQuery();

        while(rs.next()){

            if (rs.getString("uuid") == null){

                myStmt = database.prepareStatement("INSERT INTO feeder(uuid, email) VALUES(?,?)");
                myStmt.setString(1,newConnection.uuid.toString());
                myStmt.setString(2, newConnection.email);

            }else {

                myStmt = database.prepareStatement("UPDATE feeder SET email = ? where uuid = ?");
                myStmt.setString(2,newConnection.uuid.toString());
                myStmt.setString(1, newConnection.email);
            }
        }

        connections.put(newConnection.uuid, newConnection);
    }

    public String sendMessage(String message, UUID uuid) throws IOException {

        FeederConnection connection =  connections.get(uuid);
        connection.sendCommand(message);
        return connection.receiveResponse();
    }
}


