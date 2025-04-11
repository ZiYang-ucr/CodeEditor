public class HelloWorld {

    public static void main(String[] args) {
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