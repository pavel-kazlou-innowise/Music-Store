package api.model;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class Artist {

    private String name;
    private String description;
    private int id;

    public Artist(String name, String description, int id) {
        this.name = name;
        this.description = description;
        this.id = id;
    }
}
