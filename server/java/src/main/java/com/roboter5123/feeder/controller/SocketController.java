package com.roboter5123.feeder.controller;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;
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

    @Autowired
    Gson gson;

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

            JsonObject settings = new JsonObject();
            try {

                PreparedStatement myStmt = database.prepareStatement("select * from feeder f inner join schedule on schedule.schedule_id = f.schedule where f.uuid = ?");
                myStmt.setString(1, newConnection.getUuid().toString());
                ResultSet rs = myStmt.executeQuery();

                if (rs.next()) {

                    JsonObject schedule = new JsonObject();
                    schedule.add("0",gson.fromJson(rs.getString("monday"), JsonArray.class));
                    schedule.add("1",gson.fromJson(rs.getString("tuesday"), JsonArray.class));
                    schedule.add("2",gson.fromJson(rs.getString("wednesday"), JsonArray.class));
                    schedule.add("3",gson.fromJson(rs.getString("thursday"), JsonArray.class));
                    schedule.add("4",gson.fromJson(rs.getString("friday"), JsonArray.class));
                    schedule.add("5",gson.fromJson(rs.getString("saturday"), JsonArray.class));
                    schedule.add("6",gson.fromJson(rs.getString("sunday"), JsonArray.class));

                    settings.add("schedule", schedule);
                }
                newConnection.sendCommand("set#" + settings);
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

    public FeederConnection getConnection(UUID uuid) throws NullPointerException {

        return this.connections.get(uuid);
    }

    public String sendMessage(String message, UUID uuid) throws IOException, NullPointerException {

        FeederConnection connection = this.getConnection(uuid);
        connection.sendCommand(message);
        return connection.receiveResponse();
    }
}


