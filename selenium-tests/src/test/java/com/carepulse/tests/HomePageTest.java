package com.carepulse.tests;
import com.carepulse.pages.HomePage;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
public class HomePageTest {
    @Test void homeShowsCarePulseNavigation(){
        WebDriver driver=new ChromeDriver();
        try {
            HomePage page=new HomePage(driver);
            page.open();
            assertTrue(page.title().contains("CarePulse"));
            assertTrue(page.dashboardLinkVisible());
            assertEquals("http://127.0.0.1:8000/dashboard", page.dashboardLinkTarget());
        }
        finally { driver.quit(); }
    }
}

