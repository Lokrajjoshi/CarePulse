package com.carepulse.pages;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
public class HomePage {
    private final WebDriver driver;
    public HomePage(WebDriver driver){this.driver=driver;}
    public void open(){driver.get("http://127.0.0.1:8000/");}
    public String title(){return driver.getTitle();}
    public boolean dashboardLinkVisible(){return driver.findElements(By.linkText("Executive dashboard")).size()>0;}
}

