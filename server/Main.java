import com.google.gson.Gson;
import com.google.gson.JsonObject;
import spark.Request;
import sun.misc.BASE64Encoder;

import java.io.IOException;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.*;
import java.util.UUID;

import static spark.Spark.get;
import static spark.Spark.post;

public class Main {

    public static Gson gson = new Gson();
    public static Connection database;

    static {
        try {
            database = DBConnect();
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    public static void main(String[] args){

        SocketConnector socketConnector = new SocketConnector(8058);

        Thread connectorThread = new Thread(() -> {

            try {

                socketConnector.start_connector(database);


            } catch (IOException | SQLException e) {

                throw new RuntimeException(e);

            }
        });

        connectorThread.start();

        post("/command", (req, res) -> sendCommand(req, socketConnector));
        get("/settings", (req, res) -> getSettings(req, socketConnector));
        post("/setsettings", (req, res) -> setSettings(req, socketConnector));
        post("/add", (req, res) -> addTask(req, socketConnector));
        post("/dispense", (req, res) -> dispense(req, socketConnector));
        post("/login", (req, res) -> login(req));

    }

    static public Connection DBConnect() throws SQLException {

        return DriverManager.getConnection(
                "jdbc:mariadb://192.168.0.3:3306/feeder",
                "root","Password"
                );
    }

    static public String login(Request req) throws SQLException {

        String email = gson.fromJson(req.body(), JsonObject.class).get("email").getAsString();
        PreparedStatement myStmt;
        myStmt = database.prepareStatement("SELECT password from user where email = ?");
        myStmt.setString(1,email);
        ResultSet rs = myStmt.executeQuery();

        rs.next();
        String dbPassword = rs.getString("password");
        String password = gson.fromJson(req.body(), JsonObject.class).get("password").getAsString();

        if (!dbPassword.equals(password)){

            return "false";
        }

        String token = generateNewToken();
        Timestamp expirationTime = new Timestamp((long)(System.currentTimeMillis() + 8.64e+7));
        myStmt = database.prepareStatement("UPDATE user SET token = ?, validthru = ? where email = ?");
        myStmt.setString(1,token);
        myStmt.setTimestamp(2,expirationTime);
        myStmt.setString(3,email);
        myStmt.execute();
        return token;
    }

    public static String generateNewToken() {

        SecureRandom secureRandom = new SecureRandom();
        BASE64Encoder base64Encoder = new BASE64Encoder();
        byte[] randomBytes = new byte[24];
        secureRandom.nextBytes(randomBytes);
        return base64Encoder.encode(randomBytes);
    }

    public static boolean checkTokenValidity(String token, String email) throws SQLException {

        PreparedStatement myStmt = database.prepareStatement("SELECT * FROM user WHERE email = ?");
        myStmt.setString(1, email);
        ResultSet resultSet = myStmt.executeQuery();

        resultSet.next();
        Timestamp currentTime = new Timestamp(System.currentTimeMillis());

        if (resultSet.getString("token").equals("") || resultSet.getString("token") == null){

            return false;
        }

        if (resultSet.getTimestamp("validthru").compareTo(currentTime) < 1){

//          delete token from db
            deleteToken(email);
            return false;
        }

        if (!resultSet.getString("token").equals(token)){

//            Maybe delete token from db for security?
            deleteToken(email);
            return false;
        }

        return true;

    }

    public static void deleteToken(String email) throws SQLException {

        PreparedStatement myStmt = database.prepareStatement("UPDATE user SET token = null, validthru = null WHERE email = ?");
        myStmt.setString(1,email);
        myStmt.execute();
    }

    static public String addTask(Request req, SocketConnector socketConnector) throws SQLException {

        String token = gson.fromJson(req.body(), JsonObject.class).get("token").getAsString();
        String email = gson.fromJson(req.body(), JsonObject.class).get("email").getAsString();

        if(!checkTokenValidity(token,email)){

            return "Unauthorized";
        }

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

    static public String getSettings(Request req, SocketConnector socketConnector) throws SQLException {

        String token = gson.fromJson(req.body(), JsonObject.class).get("token").getAsString();
        String email = gson.fromJson(req.body(), JsonObject.class).get("email").getAsString();

        if(!checkTokenValidity(token,email)){

            return "Unauthorized";
        }

        try {

            UUID uuid = UUID.fromString(req.queryParams("uuid"));
            String message = "get#settings";
            return socketConnector.sendMessage(message, uuid);

        } catch (Exception e) {

            return e.toString();
        }
    }

    public static String setSettings(Request req, SocketConnector socketConnector) throws SQLException {

        String token = gson.fromJson(req.body(), JsonObject.class).get("token").getAsString();
        String email = gson.fromJson(req.body(), JsonObject.class).get("email").getAsString();

        if(!checkTokenValidity(token,email)){

            return "Unauthorized";
        }

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

    static public String sendCommand(Request req, SocketConnector socketConnector) throws SQLException {

        String token = gson.fromJson(req.body(), JsonObject.class).get("token").getAsString();
        String email = gson.fromJson(req.body(), JsonObject.class).get("email").getAsString();

        if(!checkTokenValidity(token,email)){

            return "Unauthorized";
        }

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

    static public String dispense(Request req, SocketConnector socketConnector) throws SQLException {

        String token = gson.fromJson(req.body(), JsonObject.class).get("token").getAsString();
        String email = gson.fromJson(req.body(), JsonObject.class).get("email").getAsString();

        if(!checkTokenValidity(token,email)){

            return "Unauthorized";
        }

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
