package com.roboter5123.feeder.beans;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.util.UUID;

public class FeederConnection {

    private int port;
    private InetAddress ip;
    private BufferedReader in;
    private PrintWriter out;
    private UUID uuid;
    private Socket client;
    private String email;

    public FeederConnection(int port, Socket client) throws IOException {

        this.client = client;
        this.port = port;
        ip = client.getInetAddress();
        in = new BufferedReader(new InputStreamReader(client.getInputStream()));
        out = new PrintWriter(client.getOutputStream(), true);
        String sentUUID = in.readLine();
        uuid = UUID.fromString(sentUUID);
    }

    public void sendCommand(String command) {

        out.println(command);
    }

    public String receiveResponse() throws IOException {

        return in.readLine();
    }

    public UUID getUuid() {

        return uuid;
    }

    public String getEmail() {

        return email;
    }
}
