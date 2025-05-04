package api.model;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class Album {

    private String title;
    private int release_year;
    private String genre;
    private int price;
    private int stock;
    private int id;
    private Artist artist;


    public Album(String title, int release_year, String genre, int price, int stock, int id, Artist artist) {
        this.title = title;
        this.release_year = release_year;
        this.genre = genre;
        this.price = price;
        this.stock = stock;
        this.id = id;
        this.artist = artist;
    }
}
