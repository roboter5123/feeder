package com.roboter5123.feeder.Service;

import com.google.gson.*;
import com.roboter5123.feeder.controller.DatabaseController;
import com.roboter5123.feeder.controller.SocketController;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
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
     * Registers an account for a first time user.
     * Hashes and salts the users password before saving it to the database.
     *
     * @param requestBody A POJO made from the request JSON must include at least email and password
     * @return A JSON that signifies the status of the registration.
     */
    @RequestMapping(value = "/api/register", method = RequestMethod.POST)
    @ResponseBody
    public String register(@RequestBody com.roboter5123.feeder.beans.RequestBody requestBody) {

        JsonObject response = new JsonObject();
        String email = requestBody.getEmail();
        String password = requestBody.getPassword();
        boolean isRegistered;

        try {

            isRegistered = isEmailRegistered(email);

        } catch (SQLException e) {

            response.add("success", new JsonPrimitive(false));
            return response.toString();
        }

        if (isRegistered) {

            response.add("success", new JsonPrimitive(false));

        } else {

            byte[] salt = generateSalt();

            try {

                password = saltAndHashPassword(password, salt);

            } catch (NoSuchAlgorithmException e) {

                response.add("success", new JsonPrimitive(false));
                return response.toString();
            }

            try {

                PreparedStatement myStmt = databaseController.prepareStatement("INSERT INTO user (email,password,salt) VALUES (?, ?, ?) ");
                myStmt.setString(1, email);
                myStmt.setString(2, password);
                myStmt.setString(3, Base64.getEncoder().encodeToString(salt));
                myStmt.execute();
                response.add("success", new JsonPrimitive(true));

            } catch (SQLException e) {

                response.add("success", new JsonPrimitive(false));
            }

        }

        return response.toString();

    }

    /**
     * @return Byte Array for salting
     */
    private byte[] generateSalt() {

        SecureRandom random = new SecureRandom();
        byte[] salt = new byte[16];
        random.nextBytes(salt);
        return salt;
    }

    /**
     * @param password Password to be hashed and salted
     * @param salt     Byte array for salting
     * @return A hashed and salted password for saving to the database or comparing to a known password
     * @throws NoSuchAlgorithmException
     */
    private String saltAndHashPassword(String password, byte[] salt) throws NoSuchAlgorithmException {

        MessageDigest md = MessageDigest.getInstance("SHA-512");
        md.update(salt);
        byte[] passwordBytes = password.getBytes(StandardCharsets.UTF_8);
        byte[] hashedPassword = md.digest(passwordBytes);
        return Base64.getEncoder().encodeToString(hashedPassword);
    }

    /**
     * @param email The email to check for in the database
     * @return Signifies if the email exists in the database.
     * @throws SQLException if the database is down.
     */
    private boolean isEmailRegistered(String email) throws SQLException {

        PreparedStatement myStmt;
        ResultSet rs;

        myStmt = databaseController.prepareStatement("SELECT email FROM user WHERE email = ?");
        myStmt.setString(1, email);
        rs = myStmt.executeQuery();
        return rs.next();

    }

    /**
     * Logs the user in with the provided email and password
     *
     * @param login A POJO made from the request JSON must include at least email and password
     * @return A token that's used to authenticate the user in all other requests
     */
    @RequestMapping(value = "/api/login", method = RequestMethod.POST)
    @ResponseBody
    public String login(@RequestBody com.roboter5123.feeder.beans.RequestBody login) {

        JsonObject response = new JsonObject();
        String email;
        String password;

        try {

            email = login.getEmail();
            password = login.getPassword();

        } catch (Exception e) {

            response.add("success", new JsonPrimitive(false));
            return response.toString();
        }

        PreparedStatement myStmt;
        byte[] salt;
        String dbPassword;

        try {

            myStmt = databaseController.prepareStatement("SELECT password, salt FROM user WHERE email = ?");
            myStmt.setString(1, email);
            ResultSet rs = myStmt.executeQuery();

            if (!rs.next()) {

                response.add("success", new JsonPrimitive(false));
                return response.toString();
            }

            dbPassword = rs.getString("password");
            salt = Base64.getDecoder().decode(rs.getString("salt"));
            password = saltAndHashPassword(password, salt);

            if (!dbPassword.equals(password)) {

                response.add("success", new JsonPrimitive(false));

            } else {

                response.add("success", new JsonPrimitive(true));
                String token = generateNewToken();
                response.add("token", new JsonPrimitive(token));
                Timestamp expirationTime = new Timestamp((long) (System.currentTimeMillis() + 8.64e+7));
                myStmt = databaseController.prepareStatement("UPDATE user SET token = ?, validthru = ? where email = ?");
                myStmt.setString(1, token);
                myStmt.setTimestamp(2, expirationTime);
                myStmt.setString(3, email);
                myStmt.execute();
                response.add("success", new JsonPrimitive(true));
            }

        } catch (SQLException | NoSuchAlgorithmException e) {

            response.add("success", new JsonPrimitive(false));

        }
        return response.toString();
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
     * Deletes the token from the database thus logging the user out
     *
     * @param logout A POJO made from the request JSON must include at least token
     * @return a bool indicating succes
     */
    @RequestMapping(value = "/api/logout", method = RequestMethod.POST)
    public String logout(@RequestBody com.roboter5123.feeder.beans.RequestBody logout) {

        JsonObject response = new JsonObject();

        response.add("success", new JsonPrimitive(deleteToken(logout.getToken())));

        return response.toString();
    }

    /**
     * Deletes a token from the database. Thus locking the user out of using all other methods but login.
     *
     * @param token Used to find the user in the database
     * @return
     */
    public boolean deleteToken(String token) {

        PreparedStatement myStmt;

        try {

            myStmt = databaseController.prepareStatement("UPDATE user SET token = null, validthru = null WHERE email = ?");
            myStmt.setString(1, token);

            return myStmt.executeUpdate() > 0;

        } catch (SQLException e) {

            return false;
        }


    }

    @RequestMapping(value = "/api/getFeeders", method = RequestMethod.POST)
    public String getFeeders(@RequestBody com.roboter5123.feeder.beans.RequestBody requestBody) throws SQLException {

        JsonObject response = new JsonObject();
        String token = requestBody.getToken();

        PreparedStatement myStmt = databaseController.prepareStatement("SELECT user.token, user.email, feederlookup.email, feederlookup.uuid, feederlookup.name from user JOIN feederlookup on user.email = feederlookup.email where user.token = ?;");
        myStmt.setString(1, token);
        ResultSet rs = myStmt.executeQuery();
        JsonObject uuids = new JsonObject();

        while (rs.next()) {

            uuids.add(rs.getString("name"), new JsonPrimitive(rs.getString("uuid")));

        }

        response.add("uuids", uuids);

        return response.toString();
    }

    @RequestMapping(value = "/api/getSchedule", method = RequestMethod.POST)
    public String getSchedule(@RequestBody com.roboter5123.feeder.beans.RequestBody requestBody) throws
            SQLException {

        JsonObject response = new JsonObject();
        String token = requestBody.getToken();
        UUID uuid = UUID.fromString(requestBody.getUuid());

        if (checkTokenInValidity(token)) {

            response.add("success", new JsonPrimitive(false));
            return response.toString();
        }

        PreparedStatement myStmt = databaseController.prepareStatement("select * from feeder f inner join schedule on schedule.schedule_id = f.schedule where f.uuid = ?");
        myStmt.setString(1, uuid.toString());
        ResultSet rs = myStmt.executeQuery();

        if (rs.next()) {

            JsonObject schedule = new JsonObject();
            schedule.add("monday", new JsonPrimitive(rs.getString("monday")));
            schedule.add("tuesday", new JsonPrimitive(rs.getString("tuesday")));
            schedule.add("wednesday", new JsonPrimitive(rs.getString("wednesday")));
            schedule.add("thursday", new JsonPrimitive(rs.getString("thursday")));
            schedule.add("friday", new JsonPrimitive(rs.getString("friday")));
            schedule.add("saturday", new JsonPrimitive(rs.getString("saturday")));
            schedule.add("sunday", new JsonPrimitive(rs.getString("sunday")));
            schedule.add("id", new JsonPrimitive(rs.getString("schedule_id")));
            response.add("schedule", schedule);
        }

        return response.toString();
    }

    @RequestMapping(value = "/api/setSchedule", method = RequestMethod.POST)
    public String setSchedule(@RequestBody com.roboter5123.feeder.beans.RequestBody requestBody) {

        JsonObject response = new JsonObject();
        UUID uuid = UUID.fromString(requestBody.getUuid());
        JsonObject args = gson.fromJson(requestBody.getArgs(), JsonObject.class);
        int scheduleId = args.get("id").getAsInt();
        args.remove("id");

        if (scheduleId <= 0){

            try {

                PreparedStatement myStmt = databaseController.prepareStatement("INSERT INTO schedule(monday,tuesday,wednesday,thursday,friday, saturday, sunday) VALUES(?,?,?,?,?,?,?);");
                setScheduleInStatement(args, myStmt);
                myStmt.execute();

                myStmt = databaseController.prepareStatement("SELECT LAST_INSERT_ID() as schedule_id");
                ResultSet rs = myStmt.executeQuery();
                rs.next();
                scheduleId = rs.getInt("schedule_id");

                myStmt = databaseController.prepareStatement("UPDATE feeder SET schedule = ? where uuid = ?");
                myStmt.setInt(1, scheduleId);
                myStmt.setString(2, uuid.toString());
                myStmt.execute();

            } catch (SQLException e) {

                response.add("success", new JsonPrimitive(false));
                return response.toString();

            }

        }else{

            try {

                PreparedStatement myStmt = databaseController.prepareStatement("UPDATE schedule SET monday = ? ,tuesday = ? ,wednesday = ? ,thursday = ? ,friday = ? ,saturday = ? ,sunday = ?  where schedule_id = ?");
                setScheduleInStatement(args, myStmt);
                myStmt.setInt(8, scheduleId);
                myStmt.execute();

            } catch (SQLException e) {

                response.add("success", new JsonPrimitive(false));
                return response.toString();
            }
        }
        JsonObject settings = new JsonObject();
        settings.add("schedule", args);

        String message = "set#" + settings;

        System.out.println(message);

        try {

            response.add("successfull", new JsonPrimitive(socketController.sendMessage(message, uuid)));

        } catch (IOException e) {

            response.add("successfull", new JsonPrimitive(false));
        }

        return response.toString();
    }

    public void setScheduleInStatement(JsonObject schedule, PreparedStatement myStmt) throws SQLException {
        myStmt.setString(1, gson.toJson(schedule.get("monday")));
        myStmt.setString(2, gson.toJson(schedule.get("tuesday")));
        myStmt.setString(3, gson.toJson(schedule.get("wednesday")));
        myStmt.setString(4, gson.toJson(schedule.get("thursday")));
        myStmt.setString(5, gson.toJson(schedule.get("friday")));
        myStmt.setString(6, gson.toJson(schedule.get("saturday")));
        myStmt.setString(7, gson.toJson(schedule.get("sunday")));
    }

    /**
     * Sends an arbitrary Command to the feeder.
     *
     * @param requestBody A POJO made from the request JSON must include at least email, token, the uuid of the device, a command and a json of args fitting the command
     * @return
     * @throws SQLException
     */
    @RequestMapping(value = "/api/command", method = RequestMethod.POST)
    public String sendCommand(@RequestBody com.roboter5123.feeder.beans.RequestBody requestBody) throws
            SQLException {

        String token = requestBody.getToken();
        UUID uuid = UUID.fromString(requestBody.getUuid());
        String command = requestBody.getCommand();
        JsonObject args = gson.fromJson(requestBody.getArgs(), JsonObject.class);

        if (checkTokenInValidity(token)) {

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

    /**
     * Dispenses for a specified amount
     *
     * @param requestBody A POJO made from the request JSON must include at least token, the uuid of the device, a command and a json of args fitting the command
     * @return
     * @throws SQLException
     */
    @RequestMapping(value = "/api/dispense", method = RequestMethod.POST)
    public String dispense(@RequestBody com.roboter5123.feeder.beans.RequestBody requestBody) throws SQLException {

        JsonObject response = new JsonObject();
        String token = requestBody.getToken();
        UUID uuid = UUID.fromString(requestBody.getUuid());
        String command = "dispense";
        JsonObject args = gson.fromJson(requestBody.getArgs(), JsonObject.class);

        if (checkTokenInValidity(token)) {

            response.add("success", new JsonPrimitive(false));
            return response.toString();
        }

        try {

            String message = command + "#" + args.get("amount").getAsString();
            return socketController.sendMessage(message, uuid);

        } catch (Exception e) {

            return e.toString();
        }

    }

    /**
     * Checks a given Cookie token for validity
     *
     * @param requestBody A POJO made from the request JSON must include at least a token
     * @return
     */
    @RequestMapping(value = "/api/checkCookie", method = RequestMethod.POST)
    public String checkCookie(@RequestBody com.roboter5123.feeder.beans.RequestBody requestBody) {

        JsonObject response = new JsonObject();
        String token = requestBody.getToken();

        try {

            response.add("success", new JsonPrimitive(!checkTokenInValidity(token)));

        } catch (SQLException e) {

            response.add("success", new JsonPrimitive(false));
        }

        return response.toString();
    }

    /**
     * Checks if a token is valid for a given email address
     *
     * @param token The token which should be checked for validity
     * @return Boolean that signifies validity
     * @throws SQLException Todo: Find out what i am supposed to write here
     */

    public boolean checkTokenInValidity(String token) throws SQLException {

        PreparedStatement myStmt = databaseController.prepareStatement("SELECT * FROM user WHERE token = ?");
        myStmt.setString(1, token);
        ResultSet resultSet = myStmt.executeQuery();

        resultSet.next();
        Timestamp currentTime = new Timestamp(System.currentTimeMillis());

        if (resultSet.getString("token").equals("") || resultSet.getString("token") == null) {

            return true;
        }

        if (resultSet.getTimestamp("validthru").compareTo(currentTime) < 1) {

//          delete token from db
            deleteToken(token);
            return true;
        }

        if (!resultSet.getString("token").equals(token)) {

//            Maybe delete token from db for security?
            deleteToken(token);
            return true;
        }

        return false;

    }

}
