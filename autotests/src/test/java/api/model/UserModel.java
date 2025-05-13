package api.model;

import lombok.Data;

@Data
public class UserModel {

    private String email;
    private String username;
    private String password;

    public UserModel(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public UserModel(String email, String username, String password) {
        this.email = email;
        this.username = username;
        this.password = password;
    }
}
