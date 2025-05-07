package api.model;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class AlbumModel {

    private String title;
    private int release_year;
    private String genre;
    private int price;
    private int stock;
    private int artist_id;


    public AlbumModel(String title, int release_year, String genre, int price, int stock, int artist_id) {
        this.title = title;
        this.release_year = release_year;
        this.genre = genre;
        this.price = price;
        this.stock = stock;
        this.artist_id = artist_id;
    }
}
