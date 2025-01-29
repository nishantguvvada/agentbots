"use client"
import { Table } from "./Table"
import { useState } from "react";
import toast from 'react-hot-toast';
import axios from "axios";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL

export const Header = () => {
    const [userQuery, setUserQuery] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const notify = () => {
        toast.success("Database refreshed.")
    }

    const handleUserQuery = async () => {
        setIsLoading(true);
        try {
            if (userQuery == "") {
                setIsLoading(false);
                toast.error("No input provided.")
                return
            }

            await axios.post(BACKEND_URL, {
                user_input:userQuery
            })

            console.log("success");
            setIsLoading(false);
            toast.success("Note created.")
            
        } catch(err) {
            console.log(err)
            toast.error("Something went wrong.")
            setIsLoading(false);
        }
    }
    return (
        <>
        <section className="bg-white">
            <div className="flex flex-col justify-center items-center gap-8 max-w-screen-xl px-4 py-8 mx-auto lg:grid lg:gap-8 lg:py-16 lg:grid-cols-12">
                <div className="mr-auto place-self-center lg:col-span-6">
                    <h1 className="text-center w-full mb-4 text-4xl font-extrabold tracking-tight leading-none md:text-5xl xl:text-6xl">JotBot</h1>
                    <h2 className="w-full text-center mb-4 text-2xl font-extrabold tracking-tight leading-none md:text-3xl xl:text-4xl">AI-powered note assistant</h2>
                    <p className="w-full text-center lg:text-left px-4 mb-6 font-light text-gray-500 lg:mb-8 md:text-lg lg:text-xl dark:text-gray-400">Effortlessly create, retrieve, and manage your notes with natural language commands, simplifying organization and boosting productivity in just a few words.</p>
                    <div className="relative px-4">
                        <textarea onChange={(e) => {setUserQuery(e.target.value)}} rows="4" className="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500" placeholder="Example: Create a note about my flight to New York next week.">
                        </textarea>
                        <div role="status" className={`absolute ${!isLoading ? "hidden" : ""} -translate-x-1/2 -translate-y-1/2 top-2/4 left-1/2`}>
                            <svg aria-hidden="true" className="w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/><path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/></svg>
                            <span className="sr-only">Loading...</span>
                        </div>
                    </div>
                    <div className="flex flex-row justify-center items-center gap-4">
                    <button onClick={handleUserQuery} className="mt-4 inline-flex items-center justify-center px-5 py-3 text-base font-medium text-center text-white rounded-lg bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300">
                        Get Started
                        <svg className="w-5 h-5 ml-2 -mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd"></path></svg>
                    </button>

                    <button onClick={notify} className="mt-4 inline-flex items-center justify-center px-5 py-3 text-base font-medium text-center text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-100 focus:ring-4 focus:ring-gray-100">
                        Refresh Table
                    </button>
                    </div> 
                </div>
                <div className="lg:mt-0 lg:col-span-6">
                   <Table/>
                </div>  
            </div>
        </section>
        </>
    )
}