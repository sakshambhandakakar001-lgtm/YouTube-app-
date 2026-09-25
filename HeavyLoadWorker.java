public class HeavyLoadWorker {
    public static void main(String[] args) {
        System.out.println("[Java Brain] Heavy Load Worker Active.");
        new Thread(() -> {
            while (true) {
                try {
                    System.gc();
                    Thread.sleep(10000);
                } catch (Exception e) {}
            }
        }).start();
    }
}
