import { Header } from "@/components/Header";
import  { Toaster } from 'react-hot-toast';

export default function Home() {
  return (
    <>
      <div>
        <Header/>
        <Toaster/>
      </div>
    </>
  );
}
