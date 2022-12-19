import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;

public class Connection {

    ServerSocket server;
    int port;
    InetAddress ip;
    BufferedReader in;
    PrintWriter out;

    public Connection(int port) {

        this.port = port;

        try {

            server = new ServerSocket(port);

        } catch (IOException e) {

            throw new RuntimeException(e);

        }
    }

    public void listenForConnection() throws IOException {

        System.out.println("Listening");
        Socket client = server.accept();
        ip = client.getInetAddress();
        in = new BufferedReader(new InputStreamReader(client.getInputStream()));
        out = new PrintWriter(client.getOutputStream(), true);
    }

    public void sendCommand(String command) {

        out.println(command);
    }

    public String receiveRespons() throws IOException {

        return in.readLine();
    }
}
