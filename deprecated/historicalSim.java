import java.util.Hashtable;
import java.util.Scanner;
import java.io.File;
import java.util.HashMap;

//pandas data reader or morningstar for data
class historicalSim {
  public Hashtable<String,stock> Table = new Hashtable<String,stock>();
  public int yearEarly;
  public int yearLate;
  //enter a name of things you own and when bought followed by folder with stock data
  public static void main (String[] args){
    historicalSim hs = new historicalSim(args);
  }

  public historicalSim(String[] args){
    try{
      this.populateTable(new File(args[1]));
      yearEarly = 9999;
      yearLate = 0000;
      HashMap<String, Double> returns = this.buyStocks(new File(args[0]));
      for(HashMap.Entry<String, Double> stock : returns.entrySet()){
      System.out.println(stock.getKey() + " returns over " + Table.get(stock.getKey()).getYearDiff() + " years: $" + Math.round(stock.getValue() * 100D) / 100D);
      }
      System.out.println("Net Beta: $" + this.getBeta(returns));
      System.out.println("Net Alpha: $" + this.getAlpha(returns));
    }
    catch(ArrayIndexOutOfBoundsException e){
      System.err.println("Please enter a file of tickers followed by a data folder");
    }
  }
  private Double getBeta(HashMap<String, Double> returns){
  double beta = 0;
    for(HashMap.Entry<String, Double> stock : returns.entrySet()){
      beta+=stock.getValue();
    }
    return Math.round(beta * 100D) / 100D;
  }
  //Takes your returns of all stocks and subtracts the returns of market from them
  private Double getAlpha(HashMap<String, Double> returns){
    double value = this.getBeta(returns) - Table.get("Market").getDiff(Integer.toString(yearLate), Integer.toString(yearEarly));
    return Math.round(value * 100D) / 100D;
  }
  private HashMap<String, Double> buyStocks(File filen){
    try{
    Scanner s1 = new Scanner(new File("" + filen));
    HashMap<String, Double> values = new HashMap<String, Double>();
    String ticker;
    String numShares;
    String finalYear;
    String initialYear;
    while(s1.hasNext()){
      ticker =s1.next();
      numShares =s1.next();
      initialYear =s1.next();
      finalYear =s1.next();
      checkYears(Integer.parseInt(initialYear), Integer.parseInt(finalYear));
      values.put(ticker, (Integer.parseInt(numShares) * Table.get(ticker).getDiff(finalYear, initialYear)));
    }
    return values;
  }
  catch (java.io.FileNotFoundException e){
    System.err.println("Please enter a fileName");
  }
  catch (java.util.NoSuchElementException e){
    System.err.println("File syntax must be: ticker num_shares buyDate(year) sellDate(year)");
  }
  return null;
  }
  //For calculating alpha. Keeps track of largest age difference of stocks
  private void checkYears(int initialYear, int finalYear){
    if(initialYear < yearEarly){
      yearEarly = initialYear;
    }
    if(finalYear > yearLate){
      yearLate = finalYear;
    }
  }
  private void populateTable(File directory){
    String[] fileNames;
    if (directory.isDirectory()){
      fileNames = directory.list();
      for(int i=0; i<fileNames.length; i++){
        parseFile(fileNames[i]);
      }
    }
    else throw new ArrayIndexOutOfBoundsException();
  }
  //this method takes data from a given file populates a Hashtable with the data then returns the table
  private void parseFile(String fileName){
    try{
    Scanner s1 = new Scanner(new File ("/Users/DavidGold/Desktop/WorkStuffs/CodeProjects/StockData/" + fileName));
    System.out.println("Loading file: "+ fileName);
    String ticker;
    String stockname;
    double initialPrice;
    while (s1.hasNextLine()){
    Scanner s2 = new Scanner(s1.nextLine());
    s2.useDelimiter(",");
    stockname = s2.next();
    if (Table.containsKey(stockname)){
      Table.get(stockname).addYear(Double.parseDouble(s2.next()), Double.parseDouble(s2.next()), fileName.substring(0,4));
    }
    else{
    Table.put(stockname, new stock(stockname, Double.parseDouble(s2.next()), Double.parseDouble(s2.next()), fileName.substring(0,4)));
    }
    s2.close();
    }
    s1.close();
  }
  catch(java.io.FileNotFoundException e){
  System.err.println("That file was not found");
  }
  }
}
class stock {
  private String ticker;
  private int yearDiff;
  HashMap<String, yearData> Allyears = new HashMap<String,yearData>();
  public stock (String ticker, double initialPrice, double finalPrice, String year){
    this.ticker = ticker;
    Allyears.put(year, new yearData(year, initialPrice, finalPrice));
  }
  public void addYear (double initialPrice, double finalPrice, String year){
    Allyears.put(year, new yearData(year, initialPrice, finalPrice));
  }
  public double getDiff(String yearf, String years){
    //This is assuming buying at start of year and selling at end
    yearDiff = Integer.parseInt(yearf)-Integer.parseInt(years);
    return Allyears.get(yearf).getFinalPrice()-Allyears.get(years).getInitialPrice();
  }
  public double getYearDiff(){
    return yearDiff;
  }
}
  class yearData {
    private String year;
    private double initialPrice;
    private double finalPrice;
    public yearData (String year, double initialPrice, double finalPrice ){
      this.year =year;
      this.initialPrice = initialPrice;
      this.finalPrice = finalPrice;
    }
    public double getFinalPrice(){
      return finalPrice;
    }
    public double getInitialPrice(){
      return initialPrice;
    }
  }
