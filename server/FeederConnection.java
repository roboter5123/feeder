import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.util.UUID;

public class FeederConnection {

    int port;
    InetAddress ip;
    BufferedReader in;
    PrintWriter out;
    UUID uuid;
    Socket client;
    String email;

    public FeederConnection(int port, Socket client) throws IOException {

        this.client = client;
        this.port = port;
        ip = client.getInetAddress();
        in = new BufferedReader(new InputStreamReader(client.getInputStream()));
        out = new PrintWriter(client.getOutputStream(), true);
        String sentUUID = in.readLine();
        uuid = UUID.fromString(sentUUID);
        email = in.readLine();
    }

    public void sendCommand(String command) {

        out.println(command);
    }

    public String receiveResponse() throws IOException {

        return in.readLine();
    }
}
