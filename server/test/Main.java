package test;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import spark.Request;

import java.io.IOException;
import java.util.UUID;

import static spark.Spark.get;
import static spark.Spark.post;

public class Main {

    public static Gson gson = new Gson();

    public static void main(String[] args){

        SocketConnector socketConnector = new SocketConnector(8058);

        Thread connectorThread = new Thread(() -> {

            try {

                socketConnector.start_connector();

            } catch (IOException e) {

                throw new RuntimeException(e);
            }
        });

        connectorThread.start();

        post("/command", (req, res) -> sendCommand(req, socketConnector));
        get("/settings", (req, res) -> getSettings(req, socketConnector));
        post("/setsettings", (req, res) -> setSettings(req, socketConnector));
        post("/add", (req, res) -> addTask(req, socketConnector));
        post("/dispense", (req, res) -> dispense(req, socketConnector));

    }

    static public String addTask(Request req, SocketConnector socketConnector) {

        try {

            JsonObject body = gson.fromJson(req.body(), JsonObject.class);
            UUID uuid = UUID.fromString(body.get("uuid").getAsString());
            String command = "add";
            String message = command + "#";
            JsonObject args = body.get("args").getAsJsonObject();
            message += args.get("day").getAsString() + "#";
            message += args.get("time").getAsString() + "#";
            message += args.get("amount").getAsString();
            System.out.println(message);
            return socketConnector.sendMessage(message, uuid);

        } catch (Exception e) {

            return e.toString();
        }
    }

    static public String getSettings(Request req, SocketConnector socketConnector){

        try {

            UUID uuid = UUID.fromString(req.queryParams("uuid"));
            String message = "get#settings";
            return socketConnector.sendMessage(message, uuid);

        } catch (Exception e) {

            return e.toString();
        }
    }

    public static String setSettings(Request req, SocketConnector socketConnector) {

        try {

            JsonObject body = gson.fromJson(req.body(), JsonObject.class);
            UUID uuid = UUID.fromString(body.get("uuid").getAsString());
            String command = "set";
            String args = body.get("args").toString();
            String message = command + "#" + args;
            System.out.println(message);
            return socketConnector.sendMessage(message, uuid);

        } catch (Exception e) {

            return e.toString();
        }

    }

    static public String sendCommand(Request req, SocketConnector socketConnector) {

        try {

            JsonObject body = gson.fromJson(req.body(), JsonObject.class);
            UUID uuid = UUID.fromString(body.get("uuid").getAsString());
            String command = body.get("command").getAsString();
            System.out.println(body);
            String args;

            if (body.get("args") instanceof JsonObject) {

                args = body.get("args").toString();

            } else {

                args = body.get("args").getAsString();

            }

            String message = command + "#" + args;
            System.out.println(message);
            return socketConnector.sendMessage(message, uuid);

        } catch (Exception e) {

            return e.toString();
        }
    }

    static public String dispense(Request req, SocketConnector socketConnector){

        try {

            JsonObject body = gson.fromJson(req.body(), JsonObject.class);
            UUID uuid = UUID.fromString(body.get("uuid").getAsString());
            String command = "dispense";
            String args = body.get("args").getAsJsonObject().get("amount").getAsString();
            String message = command + "#" + args;
            System.out.println(message);
            return socketConnector.sendMessage(message, uuid);

        } catch (Exception e) {

            return e.toString();
        }

    }
}
