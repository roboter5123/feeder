import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class Main {

    public static void main(String[] args) throws IOException {

        List<Connection> connections = new ArrayList<>();
        List<Thread> threads = new ArrayList<>();
        int port = 8058;

        connections.add(new Connection(port));
        Connection curConnection = connections.get(connections.size()-1);
        curConnection.listenForConnection();

        while (true) {

            Scanner sc = new Scanner(System.in);
            System.out.println("Enter Command for pi");
            String command = sc.nextLine();
            curConnection.sendCommand(command);
            System.out.println(curConnection.receiveRespons());
        }
    }
}
