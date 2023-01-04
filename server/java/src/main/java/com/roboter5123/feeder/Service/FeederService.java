package com.roboter5123.feeder.Service;
import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.roboter5123.feeder.controller.DatabaseController;
import com.roboter5123.feeder.controller.SocketController;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.security.SecureRandom;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.Base64;
import java.util.Map;
import java.util.UUID;

@RestController
public class FeederService {

    @Autowired
    DatabaseController databaseController;
    @Autowired
    SocketController socketController;
    @Autowired
    Gson gson;

    /**
     * Get method to send back the Frontend
     *
     * @return HTML Frontend
     */
    @RequestMapping(value = "/", method = RequestMethod.GET)
    public String getHome() {

        return "Insert HTML Frontend here";
    }

    /**
     * Logs the user in with the provided email and password
     *
     * @param login A POJO made from the request JSON must include at least email and password
     * @return A token that's used to authenticate the user in all other requests
     * @throws SQLException Todo: Find out what i am supposed to write here
     */
    @RequestMapping(value = "/api/login", method = RequestMethod.POST)
    public String login(@RequestBody com.roboter5123.feeder.beans.RequestBody login) throws SQLException {

        String email = login.getEmail();
        String password = login.getPassword();
        PreparedStatement myStmt;
        myStmt = databaseController.prepareStatement("SELECT password from user where email = ?");
        myStmt.setString(1, email);
        ResultSet rs = myStmt.executeQuery();

        rs.next();
        String dbPassword = rs.getString("password");

        if (!dbPassword.equals(password)) {

            return "false";
        }

        String token = generateNewToken();
        Timestamp expirationTime = new Timestamp((long) (System.currentTimeMillis() + 8.64e+7));
        myStmt = databaseController.prepareStatement("UPDATE user SET token = ?, validthru = ? where email = ?");
        myStmt.setString(1, token);
        myStmt.setTimestamp(2, expirationTime);
        myStmt.setString(3, email);
        myStmt.execute();
        return token;
    }

    /**
     * Generates a login token for the user and saves it in the database
     *
     * @return A login Token
     */
    public static String generateNewToken() {

        SecureRandom secureRandom = new SecureRandom();
        Base64.Encoder base64Encoder = Base64.getUrlEncoder();
        byte[] randomBytes = new byte[24];
        secureRandom.nextBytes(randomBytes);
        return base64Encoder.encodeToString(randomBytes);
    }

    /**
     * @param logout A POJO made from the request JSON must include at least email
     * @return Todo: Find out what i am supposed to write here
     * @throws SQLException Todo: Find out what i am supposed to write here
     */
    @RequestMapping(value = "/api/logout", method = RequestMethod.POST)
    public boolean logout(@RequestBody com.roboter5123.feeder.beans.RequestBody logout) throws SQLException {

        return deleteToken(logout.getEmail());

    }

    /**
     * Deletes a token from the database. Thus locking the user out of using all other methods but login.
     *
     * @param email Used to find the user in the database
     * @return Todo: Find out what i am supposed to write here
     * @throws SQLException Todo: Find out what i am supposed to write here
     */
    public boolean deleteToken(String email) throws SQLException {

        PreparedStatement myStmt = databaseController.prepareStatement("UPDATE user SET token = null, validthru = null WHERE email = ?");
        myStmt.setString(1, email);
        return myStmt.execute();
    }

    /**
     * @param requestBody A POJO made from the request JSON must include at least email, token and the uuid of the device
     * @return Settings JSON from the device
     * @throws SQLException Todo: Find out what i am supposed to write here
     * @throws IOException Todo: Find out what i am supposed to write here
     */
    @RequestMapping(value = "/api/getSettings", method = RequestMethod.GET)
    public String getSettings(@RequestBody com.roboter5123.feeder.beans.RequestBody requestBody) throws SQLException, IOException {

        String token = requestBody.getToken();
        String email = requestBody.getEmail();
        UUID uuid = UUID.fromString(requestBody.getUuid());

        if (checkTokenInValidity(token, email)) {

            return "Unauthorized";
        }

        String message = "get#settings";
        return socketController.sendMessage(message, uuid);
    }

    /**
     * @param requestBody A POJO made from the request JSON must include at least email, token and the uuid of the device
     * @return Todo: Find out what i am supposed to write here
     * @throws SQLException Todo: Find out what i am supposed to write here
     * @throws IOException Todo: Find out what i am supposed to write here
     */
    @RequestMapping(value = "/api/setSettings", method = RequestMethod.POST)
    public String setSettings(@RequestBody com.roboter5123.feeder.beans.RequestBody requestBody) throws SQLException, IOException {

        String token = requestBody.getToken();
        String email = requestBody.getEmail();
        UUID uuid = UUID.fromString(requestBody.getUuid());

        if (checkTokenInValidity(token, email)) {

            return "Unauthorized";
        }

        String command = "set";
        String message = command + "#" + requestBody.getArgs();
        System.out.println(message);
        return socketController.sendMessage(message, uuid);

    }

    /**
     * Adds a task to the devices schedule.
     *
     * @param requestBody A POJO made from the request JSON must include at least email, token
     *                    , the uuid of the device and a json String which has to include
     *                    day, time and amount
     * @return Todo: Find out what i am supposed to write here
     * @throws SQLException Todo: Find out what i am supposed to write here
     */
    @RequestMapping(value = "/api/add", method = RequestMethod.POST)
    public String addTask(@RequestBody com.roboter5123.feeder.beans.RequestBody requestBody) throws SQLException {

        String token = requestBody.getToken();
        String email = requestBody.getEmail();
        UUID uuid = UUID.fromString(requestBody.getUuid());
        JsonObject args = gson.fromJson(requestBody.getArgs(), JsonObject.class);

        if (checkTokenInValidity(token, email)) {

            return "Unauthorized";
        }

        try {

            String command = "add";
            String message = command + "#";

            message += args.get("day").getAsString() + "#";
            message += args.get("time").getAsString() + "#";
            message += args.get("amount").getAsString();
            System.out.println(message);
            return socketController.sendMessage(message, uuid);

        } catch (Exception e) {

            return e.toString();
        }
    }

    /**
     * Sends an arbitrary Command to the feeder.
     *
     * @param requestBody  A POJO made from the request JSON must include at least email, token, the uuid of the device, a command and a json of args fitting the command
     * @return Todo: Find out what i am supposed to write here
     * @throws SQLException Todo: Find out what i am supposed to write here
     */
    @RequestMapping(value = "/api/command", method = RequestMethod.POST)
    public String sendCommand(@RequestBody com.roboter5123.feeder.beans.RequestBody requestBody) throws SQLException {

        String token = requestBody.getToken();
        String email = requestBody.getEmail();
        UUID uuid = UUID.fromString(requestBody.getUuid());
        String command = requestBody.getCommand();
        JsonObject args = gson.fromJson(requestBody.getArgs(), JsonObject.class);

        if (checkTokenInValidity(token, email)) {

            return "Unauthorized";
        }

        StringBuilder message = new StringBuilder(command);

        Map<String, JsonElement> argsMap = args.asMap();

        for (JsonElement arg : argsMap.values()) {

            message.append("#").append(arg);
        }

        try {

            return socketController.sendMessage(message.toString(), uuid);

        } catch (Exception e) {

            return e.toString();
        }
    }

    @RequestMapping(value = "/api/dispense", method = RequestMethod.POST)
    public String dispense(@RequestBody com.roboter5123.feeder.beans.RequestBody requestBody) throws SQLException {

        String token = requestBody.getToken();
        String email = requestBody.getEmail();
        UUID uuid = UUID.fromString(requestBody.getUuid());
        String command = "dispense";
        JsonObject args = gson.fromJson(requestBody.getArgs(), JsonObject.class);

        if(checkTokenInValidity(token, email)){

            return "Unauthorized";
        }

        try {

            String message = command + "#" + args.get("amount").getAsString();
            return socketController.sendMessage(message, uuid);

        } catch (Exception e) {

            return e.toString();
        }

    }

    /**
     * Checks if a token is valid for a given email address
     *
     * @param token The token which should be checked for validity
     * @param email The email of the user whose token should be checked.
     * @return Boolean that signifies validity
     * @throws SQLException Todo: Find out what i am supposed to write here
     */
    public boolean checkTokenInValidity(String token, String email) throws SQLException {

        PreparedStatement myStmt = databaseController.prepareStatement("SELECT * FROM user WHERE email = ?");
        myStmt.setString(1, email);
        ResultSet resultSet = myStmt.executeQuery();

        resultSet.next();
        Timestamp currentTime = new Timestamp(System.currentTimeMillis());

        if (resultSet.getString("token").equals("") || resultSet.getString("token") == null) {

            return true;
        }

        if (resultSet.getTimestamp("validthru").compareTo(currentTime) < 1) {

//          delete token from db
            deleteToken(email);
            return true;
        }

        if (!resultSet.getString("token").equals(token)) {

//            Maybe delete token from db for security?
            deleteToken(email);
            return true;
        }

        return false;

    }

}
