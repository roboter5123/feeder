package com.roboter5123.feeder.controller;

import com.roboter5123.feeder.beans.FeederConnection;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;

import java.io.IOException;
import java.net.ServerSocket;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.UUID;

@Controller
public class SocketController extends Thread {

    ServerSocket server;
    int port;
    HashMap<UUID, FeederConnection> connections;
    boolean running;
    @Autowired
    private final DatabaseController database;

    public SocketController(DatabaseController database) {

        this.database = database;
        this.port = 8058;
        this.connections = new HashMap<>();

        try {

            this.server = new ServerSocket(port);

        } catch (IOException e) {

            throw new RuntimeException(e);
        }

        this.start();
    }

    public void run() {

        running = true;

        while (running) {

            FeederConnection newConnection;

            try {
                newConnection = new FeederConnection(port, server.accept());

            } catch (IOException e) {

                throw new RuntimeException(e);
            }

            try {

                addConnection(newConnection);

            } catch (SQLException e) {

                throw new RuntimeException(e);
            }
        }
    }

    public void addConnection(FeederConnection newConnection) throws SQLException {


        PreparedStatement myStmt = database.prepareStatement("SELECT * FROM feeder where uuid = ?");
        myStmt.setString(1, newConnection.getUuid().toString());
        ResultSet rs = myStmt.executeQuery();

        if (!rs.next()) {

            myStmt = database.prepareStatement("INSERT INTO feeder(uuid) VALUES(?)");
            myStmt.setString(1, newConnection.getUuid().toString());
            myStmt.execute();
        }

        this.connections.put(newConnection.getUuid(), newConnection);
        System.out.println("connected with " + newConnection.getUuid().

                toString());
    }

    public FeederConnection getConnection(UUID uuid) {

        return this.connections.get(uuid);
    }

    public String sendMessage(String message, UUID uuid) throws IOException {

        FeederConnection connection = this.getConnection(uuid);
        connection.sendCommand(message);
        return connection.receiveResponse();
    }
}


