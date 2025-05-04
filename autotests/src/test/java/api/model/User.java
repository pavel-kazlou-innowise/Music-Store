package api.model;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class User {

    private String email;
    private String username;
    private int id;
    private String is_active;
    private String is_admin;
    private String created_at;

    public User (String email, String username, int id, String is_active, String is_admin, String created_at) {
        this.email = email;
        this.username = username;
        this.id = id;
        this.is_active = is_active;
        this.is_admin = is_admin;
        this.created_at = created_at;
    }
}
