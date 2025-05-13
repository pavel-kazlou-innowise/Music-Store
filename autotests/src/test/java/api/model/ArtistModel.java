package api.model;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class ArtistModel {

    private String name;
    private String description;

    public ArtistModel(String name, String description) {
        this.name = name;
        this.description = description;
    }
}
