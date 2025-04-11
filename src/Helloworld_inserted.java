public class HelloWorld {

    public static void main(String[] args) {
            
            switch(day) {
                case 1: System.out.println("Monday"); break;
                case 2: System.out.println("Tuesday"); break;
                default: System.out.println("Other day");
            }
            
        System.out.println("Hello, World!");
        int day = 2; // <--- switch 插入之后
    }

    public int add(int a, int b) {
        return a + b;
    }

    private void greet(String name) {
        System.out.println("Hello, " + name);
    }
}