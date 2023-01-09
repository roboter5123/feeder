package com.roboter5123.feeder.controller;
import org.springframework.stereotype.Controller;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

@Controller
public class DatabaseController {

    Connection connection;

    public DatabaseController() throws SQLException {

        this.connection = DriverManager.getConnection(
                "jdbc:mysql://roboter5123.com:3306/feeder",
                "root", "Password"
        );

    }

    public PreparedStatement prepareStatement(String sql) throws SQLException {

        return connection.prepareStatement(sql);
    }
}
